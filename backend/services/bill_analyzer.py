"""
Bill Analyzer Service for HealthNexus AI
Extracts and analyzes medical bills
"""
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict

try:
    import fitz  # PyMuPDF for PDF processing
except Exception:  # pragma: no cover - optional dependency guard
    fitz = None

try:
    from pdf2image import convert_from_bytes
except Exception:  # pragma: no cover - optional dependency guard
    convert_from_bytes = None

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional dependency guard
    PdfReader = None

from utils.ocr_processor import ocr_from_image_bytes

logger = logging.getLogger(__name__)

# Amount regex pattern (supports both "1,25,000" and "125000")
AMOUNT_RE = re.compile(
    r"(?:rs\.?|re\.?|res\.?|inr|₹)?\s*(?P<amount>(?:\d{1,3}(?:[,\s]\d{3})+|\d+)(?:\.\d{1,2})?)",
    re.IGNORECASE,
)

# Market rate reference for overcharge detection (in INR)
MARKET_RATES = {
    'consultation': 1500,
    'room rent': 5000,
    'icu': 16000,
    'ot charges': 20000,
    'surgery': 50000,
    'anesthesia': 12000,
    'nursing': 2500,
    'diagnostics_lab': 3000,
    'imaging': 7000,
    'pharmacy_medicines': 10000,
    'physiotherapy': 1500,
    'implant': 65000,
    'dressing': 5000,
    'admin_misc': 5000,
    'misc': 10000
}

CATEGORY_KEYWORDS = {
    'consultation': ['consultation', 'doctor fee', 'visit fee', 'physician'],
    'room rent': ['room charges', 'room rent', 'bed charge', 'ward charge', 'private room', 'semi-private'],
    'icu': ['icu', 'intensive care', 'ccu', 'hicu'],
    'ot charges': ['ot charges', 'operation theatre', 'operation theater', 'theatre charges'],
    'surgery': ['surgery', 'surgical procedure', 'operation fee', 'procedure fee'],
    'anesthesia': ['anesthesia', 'anaesthesia', 'anesthetic'],
    'nursing': ['nursing charges', 'nursing fee', 'nurse'],
    'diagnostics_lab': ['blood test', 'cbc', 'lft', 'kft', 'thyroid', 'lipid', 'pathology', 'lab', 'test'],
    'imaging': ['x-ray', 'xray', 'ct scan', 'mri', 'ultrasound', 'usg', 'ecg', 'scan'],
    'pharmacy_medicines': ['medicines', 'pharmacy', 'injection', 'iv fluid', 'drug', 'fluids', 'syrup'],
    'physiotherapy': ['physiotherapy', 'physio', 'rehab'],
    'implant': ['implant', 'stent', 'plate', 'screw', 'prosthesis'],
    'dressing': ['dressing', 'bandage', 'gauze', 'wound care'],
    'admin_misc': ['administrative', 'admin', 'registration', 'waste disposal', 'bio-medical', 'service charge'],
    'misc': ['misc', 'miscellaneous'],
}

HEADER_FOOTER_KEYWORDS = [
    'apollo hospitals', 'indraprastha', 'sarita vihar', 'delhi', 'phone:', 'license:',
    'medical bill', 'invoice number', 'bill date', 'patient name', 'patient id',
    'room type', 'itemized charges', 'description qty amount', 'subtotal',
    'gst (', 'service charge', 'total amount:', 'payment due', 'for queries:',
    'hospital', 'clinic', 'tax', 'terms & conditions', 'discharge'
]


def _normalize_description_key(description: str) -> str:
    """Normalize description for duplicate grouping."""
    text = (description or '').lower()
    text = re.sub(r'\b(rs|re|res|inr|qty|quantity|no|nos|mrp)\b', ' ', text)
    text = re.sub(r'\b\d+\b', ' ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _categorize_item(description: str) -> str:
    """Map description to best category for benchmark comparison."""
    text = (description or '').lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return 'misc'


def _severity_from_ratio(ratio: float) -> str:
    if ratio >= 3.0:
        return 'high'
    if ratio >= 2.2:
        return 'medium'
    return 'low'


def normalize_amount(s: Optional[str]) -> float:
    """Convert string amount to float"""
    if not s:
        return 0.0
    s2 = s.replace(',', '').replace(' ', '')
    try:
        return float(s2)
    except Exception:
        s3 = re.sub(r'[^\d\.]', '', s2)
        try:
            return float(s3) if s3 else 0.0
        except Exception:
            return 0.0


def parse_text_lines(raw_text: str) -> List[Dict[str, Any]]:
    """
    Parse bill text line by line, cleanly filtering header/footer/metadata.
    """
    lines = raw_text.splitlines()
    parsed: List[Dict[str, Any]] = []
    line_id = 1

    for ln in lines:
        ln_clean = (ln or '').strip()
        if not ln_clean:
            continue

        ln_lower = ln_clean.lower()

        # Stop at summary/footer totals section
        if any(f in ln_lower for f in [
            'subtotal:', 'total amount:', 'balance due:', 'amount paid:',
            'gst (5%)', 'service charge:', 'payment due', 'payment instructions:'
        ]):
            continue

        # Filter header/metadata/demographics lines explicitly
        if any(k in ln_lower for k in [
            'apollo hospitals', 'indraprastha', 'sarita vihar', 'phone:', 'license:',
            'invoice number:', 'bill date:', 'admission date:', 'discharge date:',
            'patient name:', 'patient id:', 'age/gender:', 'room type:',
            'medical bill', 'itemized charges', 'description qty amount', 'for queries:'
        ]):
            continue

        # Ignore header lines containing 'description' or 'particulars'
        if 'description' in ln_lower or 'particulars' in ln_lower:
            continue

        # Ignore lines without at least 3 alphabetic characters (e.g. orphan numbers, dates, line IDs)
        alpha_chars = len(re.findall(r'[a-zA-Z]', ln_clean))
        if alpha_chars < 3:
            continue

        # Extract number tokens from line
        amount_matches = list(re.finditer(r'(?:rs\.?|re\.?|res\.?|inr|₹)?\s*([\d,]{2,}(?:\.\d{1,2})?)', ln_clean, re.IGNORECASE))
        if not amount_matches:
            continue

        # Last amount token on line is total line charge
        last_match = amount_matches[-1]
        amt_val = normalize_amount(last_match.group(1))

        if amt_val <= 0 or amt_val > 5000000:
            continue

        # Description text is everything up to the final rate/amount numbers
        raw_desc = ln_clean[:last_match.start()].strip()

        # Clean serial number at start e.g. "1 Room Charges..." -> "Room Charges..."
        raw_desc = re.sub(r'^\d+[\s\.\)-]+', '', raw_desc)

        # Extract trailing numbers (rate / qty) from raw_desc
        trailing_nums = re.findall(r'[\d,]+', raw_desc)
        quantity = 1
        if len(trailing_nums) >= 2:
            try:
                possible_qty = int(trailing_nums[-2])
                if 1 <= possible_qty <= 30:
                    quantity = possible_qty
            except Exception:
                pass
        elif len(trailing_nums) == 1:
            try:
                possible_qty = int(trailing_nums[-1])
                if 1 <= possible_qty <= 30:
                    quantity = possible_qty
            except Exception:
                pass

        # Strip rate/quantity numbers from end of description
        clean_desc = re.sub(r'(?:\s+[\d,]+)+$', '', raw_desc).strip()
        if len(clean_desc) < 3:
            clean_desc = raw_desc

        # Remove currency symbols
        clean_desc = re.sub(r'\b(rs\.?|re\.?|res\.?|inr|₹)\b', '', clean_desc, flags=re.IGNORECASE).strip()

        parsed.append({
            "line_id": line_id,
            "description": clean_desc[:200],
            "raw_line": ln_clean,
            "amount": round(amt_val, 2),
            "quantity": max(1, quantity),
            "date": None,
        })
        line_id += 1

    return parsed


def analyze_line_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze bill line items for anomalies
    """
    flagged_items: List[Dict[str, Any]] = []
    total_savings = 0.0

    # ---------- Duplicate detection ----------
    duplicate_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for item in items:
        key = _normalize_description_key(item.get('description', ''))
        if key and len(key) >= 3:
            duplicate_groups[key].append(item)

    for normalized_desc, group_items in duplicate_groups.items():
        if len(group_items) < 2:
            continue

        amounts = [float(it.get('amount', 0) or 0) for it in group_items]
        min_amt = min(amounts) if amounts else 0.0
        max_amt = max(amounts) if amounts else 0.0
        avg_amt = sum(amounts) / len(amounts) if amounts else 0.0
        amount_similarity = 1.0 if avg_amt <= 0 else max(
            0.0, 1.0 - ((max_amt - min_amt) / avg_amt))

        # Confidence score for duplicate suspicion
        confidence = 0.65 + 0.25 * amount_similarity
        confidence = min(0.98, round(confidence, 2))

        # First occurrence is assumed valid; remaining are potential duplicate billing
        duplicate_count = len(group_items) - 1
        potential_saving = round(min_amt * duplicate_count, 2)
        total_savings += potential_saving

        flagged_items.append({
            'type': 'duplicate',
            'severity': 'high' if confidence >= 0.8 else 'medium',
            'confidence': confidence,
            'line_ids': [it['line_id'] for it in group_items],
            'description': group_items[0].get('description', normalized_desc),
            'amount': round(avg_amt, 2),
            'category': _categorize_item(group_items[0].get('description', '')),
            'issue': f"'{group_items[0].get('description', normalized_desc)}' appears {len(group_items)} times; potential duplicate charge of ₹{potential_saving:,.0f}",
            'potential_saving': potential_saving,
        })

    # ---------- Overcharge detection ----------
    flagged_line_ids = {
        line_id for f in flagged_items for line_id in f.get('line_ids', [])}
    for item in items:
        amount = float(item.get('amount', 0) or 0)
        if amount <= 0:
            continue

        qty = max(1, int(item.get('quantity') or 1))
        category = _categorize_item(item.get('description', ''))
        unit_benchmark = float(MARKET_RATES.get(category, MARKET_RATES['misc']))
        total_benchmark = unit_benchmark * qty
        ratio = amount / total_benchmark if total_benchmark > 0 else 1.0

        # Trigger threshold for suspicious overcharge (must be at least 2.5x benchmark)
        if ratio < 2.5:
            continue

        # Avoid double-flagging same line if already included in duplicate
        if item.get('line_id') in flagged_line_ids:
            continue

        severity = _severity_from_ratio(ratio)
        confidence = min(0.95, round(0.50 + min(ratio / 4.0, 0.40), 2))
        potential_saving = round(max(0.0, amount - total_benchmark), 2)
        total_savings += potential_saving

        flagged_items.append({
            'type': 'overcharge',
            'severity': severity,
            'confidence': confidence,
            'line_ids': [item['line_id']],
            'description': item['description'],
            'amount': amount,
            'category': category,
            'market_rate': total_benchmark,
            'issue': f"Charged ₹{amount:,.0f} for {item['description']}; estimated benchmark rate is ~₹{total_benchmark:,.0f} ({ratio:.1f}x)",
            'potential_saving': potential_saving,
        })

    # ---------- Scoring summary ----------
    duplicate_count = sum(
        1 for f in flagged_items if f.get('type') == 'duplicate')
    overcharge_count = sum(
        1 for f in flagged_items if f.get('type') == 'overcharge')
    high_risk_count = sum(
        1 for f in flagged_items if f.get('severity') == 'high')
    medium_risk_count = sum(
        1 for f in flagged_items if f.get('severity') == 'medium')
    low_risk_count = sum(
        1 for f in flagged_items if f.get('severity') == 'low')

    average_confidence = round(
        (sum(float(f.get('confidence', 0))
         for f in flagged_items) / len(flagged_items))
        if flagged_items else 0.0,
        2,
    )

    # Weighted risk score out of 100
    risk_numerator = (high_risk_count * 25) + \
        (medium_risk_count * 15) + (low_risk_count * 8)
    risk_denominator = max(1, len(items) * 10)
    risk_score = int(
        min(100, round((risk_numerator / risk_denominator) * 100)))

    # Calculate totals
    computed_total = sum(item['amount'] for item in items)

    return {
        'total_items': len(items),
        'flagged_items': flagged_items,
        'flagged_count': len(flagged_items),
        'duplicate_count': duplicate_count,
        'overcharge_count': overcharge_count,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'average_confidence': average_confidence,
        'risk_score': risk_score,
        'computed_total': round(computed_total, 2),
        'potential_savings': round(total_savings, 2)
    }


def extract_metadata(raw_text: str) -> Dict[str, Any]:
    """
    Extract bill metadata (hospital name, date, invoice number)

    Args:
        raw_text: OCR text

    Returns:
        Metadata dict
    """
    metadata = {
        'hospital_name': None,
        'invoice_number': None,
        'bill_date': None
    }

    lines = raw_text.splitlines()

    # Extract hospital name (usually in first few lines)
    for line in lines[:10]:
        if any(keyword in line.lower() for keyword in ['hospital', 'clinic', 'medical', 'healthcare']):
            metadata['hospital_name'] = line.strip()
            break

    # Extract invoice number
    invoice_match = re.search(
        r'(invoice|bill|receipt)\s*#?\s*:?\s*(\w+)', raw_text, re.IGNORECASE)
    if invoice_match:
        metadata['invoice_number'] = invoice_match.group(2)

    # Extract date
    date_match = re.search(
        r'date\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{4})', raw_text, re.IGNORECASE)
    if date_match:
        metadata['bill_date'] = date_match.group(1)

    return metadata


def extract_pdf_text_by_layout(file_bytes: bytes) -> str:
    """Extract text from PDF preserving horizontal layout line structure."""
    if fitz is None:
        return ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_lines = []
        for page in doc:
            words = page.get_text("words")  # (x0, y0, x1, y1, word, block_no, line_no, word_no)
            if not words:
                continue
            line_dict = {}
            for w in words:
                # Group words on same visual line by rounding y0 coordinate
                y_key = round(w[1] / 4.0) * 4.0
                line_dict.setdefault(y_key, []).append((w[0], w[4]))

            sorted_y = sorted(line_dict.keys())
            for y in sorted_y:
                # Sort words in line horizontally by x0
                line_words = sorted(line_dict[y], key=lambda item: item[0])
                line_text = " ".join(w[1] for w in line_words)
                page_lines.append(line_text)
        doc.close()
        return "\n".join(page_lines)
    except Exception as e:
        logger.error(f"Failed to extract PDF layout: {e}")
        return ""


def process_pdf_bill(file_bytes: bytes) -> Dict[str, Any]:
    """
    Process PDF bill

    Args:
        file_bytes: PDF file bytes

    Returns:
        Analysis result
    """
    try:
        # Fallback path when PyMuPDF is unavailable
        if fitz is None:
            # 1) Try pure-text extraction via pypdf (no external system deps)
            if PdfReader is not None:
                import io

                reader = PdfReader(io.BytesIO(file_bytes))
                text_parts: List[str] = []
                for page in reader.pages[:5]:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text_parts.append(page_text)
                full_text = "\n".join(text_parts).strip()
                if full_text:
                    return process_bill_text(full_text, 90.0)

            # 2) If no text layer, OCR rendered pages via pdf2image
            if convert_from_bytes is None:
                return {
                    'status': 'error',
                    'error': 'PDF processing unavailable: install PyMuPDF, or install pypdf / pdf2image with poppler support'
                }

            pages = convert_from_bytes(
                file_bytes, dpi=220, first_page=1, last_page=3)
            full_text_parts: List[str] = []
            confidences: List[float] = []

            for page_img in pages:
                import io

                buf = io.BytesIO()
                page_img.save(buf, format="PNG")
                text, confidence = ocr_from_image_bytes(buf.getvalue())
                if text and text.strip():
                    full_text_parts.append(text)
                confidences.append(float(confidence or 0.0))

            full_text = "\n".join(full_text_parts).strip()
            avg_confidence = round(
                (sum(confidences) / len(confidences)) if confidences else 0.0,
                1,
            )

            if not full_text:
                return {
                    'status': 'error',
                    'error': 'No text extracted from PDF pages'
                }

            return process_bill_text(full_text, avg_confidence)

        # Extract layout-preserved text from PDF
        full_text = extract_pdf_text_by_layout(file_bytes)

        if not full_text.strip():
            # If no layout text, fallback to standard PyMuPDF text
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            full_text = "".join(page.get_text() for page in pdf_doc)
            pdf_doc.close()

        if not full_text.strip():
            # If still no text (scanned image inside PDF), try OCR on first page
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            page = pdf_doc[0]
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            full_text, confidence = ocr_from_image_bytes(img_bytes)
            pdf_doc.close()
        else:
            confidence = 95.0  # High confidence for extracted text

        return process_bill_text(full_text, confidence)

        return process_bill_text(full_text, confidence)

    except Exception as e:
        logger.error("PDF processing failed: %s", e)
        return {
            'status': 'error',
            'error': str(e)
        }


def process_image_bill(file_bytes: bytes) -> Dict[str, Any]:
    """
    Process image bill (JPG, PNG, HEIC)

    Args:
        file_bytes: Image file bytes

    Returns:
        Analysis result
    """
    try:
        # Perform OCR
        text, confidence = ocr_from_image_bytes(file_bytes)

        return process_bill_text(text, confidence)

    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


def process_bill_text(raw_text: str, ocr_confidence: float) -> Dict[str, Any]:
    """
    Process extracted bill text

    Args:
        raw_text: Extracted text
        ocr_confidence: OCR confidence score

    Returns:
        Complete analysis result
    """
    if not raw_text.strip():
        return {
            'status': 'error',
            'error': 'No text extracted from bill'
        }

    # Extract metadata
    metadata = extract_metadata(raw_text)

    # Parse line items
    line_items = parse_text_lines(raw_text)

    # Analyze items
    analysis = analyze_line_items(line_items)

    return {
        'status': 'success',
        'metadata': metadata,
        'raw_text': raw_text[:1000],  # First 1000 chars
        'ocr_confidence': round(ocr_confidence, 1),
        'line_items': line_items,
        'analysis': analysis
    }


def analyze_bill_file(file_storage, file_extension: str) -> Dict[str, Any]:
    """
    Main entry point for bill analysis

    Args:
        file_storage: Flask FileStorage object or file bytes
        file_extension: File extension (.pdf, .jpg, etc.)

    Returns:
        Analysis result
    """
    try:
        # Read file bytes
        if hasattr(file_storage, 'read'):
            file_bytes = file_storage.read()
        else:
            file_bytes = file_storage

        # Process based on file type
        if file_extension.lower() in ['.pdf']:
            return process_pdf_bill(file_bytes)
        elif file_extension.lower() in ['.jpg', '.jpeg', '.png', '.heic']:
            return process_image_bill(file_bytes)
        else:
            return {
                'status': 'error',
                'error': f'Unsupported file format: {file_extension}'
            }

    except Exception as e:
        logger.error(f"Bill analysis failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
