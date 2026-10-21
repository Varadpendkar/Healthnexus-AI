import React, { useState } from "react";
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Divider,
} from "@mui/material";
import UploadIcon from "@mui/icons-material/CloudUpload";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import CheckIcon from "@mui/icons-material/CheckCircle";
import WarningIcon from "@mui/icons-material/Warning";
import ReceiptIcon from "@mui/icons-material/Receipt";
import axios from "axios";
import Navigation from "../components/Navigation";
import ChatbotWidget from "../components/ChatbotWidget";

interface LineItem {
  line_id: number;
  description: string;
  amount: number;
  quantity: number;
  date: string | null;
  raw_line: string;
}

interface FlaggedItem {
  type: string;
  severity?: "low" | "medium" | "high";
  confidence?: number;
  category?: string;
  line_ids: number[];
  description: string;
  amount: number;
  issue: string;
  potential_saving: number;
  market_rate?: number;
}

interface BillAnalysis {
  total_items: number;
  flagged_items: FlaggedItem[];
  flagged_count: number;
  duplicate_count?: number;
  overcharge_count?: number;
  high_risk_count?: number;
  medium_risk_count?: number;
  low_risk_count?: number;
  average_confidence?: number;
  risk_score?: number;
  computed_total: number;
  potential_savings: number;
}

interface BillResult {
  status: string;
  metadata: {
    hospital_name: string | null;
    invoice_number: string | null;
    bill_date: string | null;
  };
  raw_text: string;
  ocr_confidence: number;
  line_items: LineItem[];
  analysis: BillAnalysis;
}

const BillBusterPage: React.FC = () => {
  const API_BASE = "http://127.0.0.1:5001";
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<BillResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError("Please select a file");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      // Simple OCR-based synchronous analysis
      const response = await axios.post(
        `${API_BASE}/api/bill-buster/upload`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 120000,
        },
      );

      if (response.data?.success && response.data?.status === "success") {
        setResult(response.data as BillResult);
      } else {
        setError(response.data?.error || "Bill analysis failed");
      }
    } catch (err: any) {
      console.error("Analysis error:", err);
      setError(
        err.response?.data?.error ||
          "Failed to analyze bill. Please try again.",
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const severityColor = (
    severity?: string,
  ): "default" | "error" | "warning" | "info" => {
    if (severity === "high") return "error";
    if (severity === "medium") return "warning";
    if (severity === "low") return "info";
    return "default";
  };

  const getLineSeverity = (
    lineId: number,
  ): "none" | "low" | "medium" | "high" => {
    const matches =
      result?.analysis.flagged_items.filter((item) =>
        item.line_ids.includes(lineId),
      ) || [];

    if (!matches.length) return "none";
    if (matches.some((m) => m.severity === "high")) return "high";
    if (matches.some((m) => m.severity === "medium")) return "medium";
    return "low";
  };

  const getStatusIcon = (lineId: number) => {
    const severity = getLineSeverity(lineId);
    if (severity === "high") return <WarningIcon color="error" />;
    if (severity === "medium") return <WarningIcon color="warning" />;
    if (severity === "low") return <WarningIcon color="info" />;
    return <CheckIcon color="success" />;
  };

  return (
    <>
      <Navigation />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ textAlign: "center", mb: 4 }}>
          <ReceiptIcon sx={{ fontSize: 64, color: "primary.main", mb: 2 }} />
          <Typography variant="h3" gutterBottom fontWeight="bold">
            Bill Buster
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Upload your medical bill and detect errors, overcharges, and
            potential savings
          </Typography>
        </Box>

        {/* Upload Section */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Typography variant="h6" gutterBottom>
                  Upload Medical Bill
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Supported formats: PDF, JPG, PNG, HEIC (Max 10MB)
                </Typography>
                <input
                  accept=".pdf,.jpg,.jpeg,.png,.heic"
                  style={{ display: "none" }}
                  id="bill-file-input"
                  type="file"
                  onChange={handleFileSelect}
                />
                <label htmlFor="bill-file-input">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<UploadIcon />}
                    fullWidth
                    sx={{ mb: 2 }}
                  >
                    Choose File
                  </Button>
                </label>
                {selectedFile && (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Selected: {selectedFile.name} (
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </Alert>
                )}
              </Grid>
              <Grid item xs={12} md={4}>
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    height: "100%",
                    justifyContent: "center",
                  }}
                >
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleAnalyze}
                    disabled={!selectedFile || isAnalyzing}
                    fullWidth
                    sx={{
                      py: 2,
                      background:
                        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                      "&:hover": {
                        background:
                          "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
                      },
                    }}
                  >
                    {isAnalyzing ? (
                      <>
                        <CircularProgress
                          size={24}
                          sx={{ mr: 1, color: "white" }}
                        />
                        Analyzing...
                      </>
                    ) : (
                      "Analyze Bill"
                    )}
                  </Button>
                </Box>
              </Grid>
            </Grid>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Results Section */}
        {result && (
          <>
            {/* Summary Card */}
            <Card
              sx={{
                mb: 3,
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                color: "white",
              }}
            >
              <CardContent>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={3}>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      Total Amount
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      ₹{result.analysis.computed_total.toLocaleString("en-IN")}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      High-Risk Flags
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {result.analysis.high_risk_count ?? 0}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      Potential Savings
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      ₹
                      {result.analysis.potential_savings.toLocaleString(
                        "en-IN",
                      )}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      Detector Confidence
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {Math.round(
                        (result.analysis.average_confidence ?? 0) * 100,
                      )}
                      %
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🤖 AI Billing Risk Detector
                </Typography>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="text.secondary">
                      Risk Score
                    </Typography>
                    <Typography
                      variant="h4"
                      fontWeight="bold"
                      color="error.main"
                    >
                      {result.analysis.risk_score ?? 0}/100
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={8}>
                    <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                      <Chip
                        color="error"
                        label={`High: ${result.analysis.high_risk_count ?? 0}`}
                      />
                      <Chip
                        color="warning"
                        label={`Medium: ${result.analysis.medium_risk_count ?? 0}`}
                      />
                      <Chip
                        color="info"
                        label={`Low: ${result.analysis.low_risk_count ?? 0}`}
                      />
                      <Chip
                        variant="outlined"
                        label={`Duplicates: ${result.analysis.duplicate_count ?? 0}`}
                      />
                      <Chip
                        variant="outlined"
                        label={`Overcharges: ${result.analysis.overcharge_count ?? 0}`}
                      />
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Metadata */}
            {(result.metadata.hospital_name || result.metadata.bill_date) && (
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Bill Information
                  </Typography>
                  <Grid container spacing={2}>
                    {result.metadata.hospital_name && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">
                          Hospital
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {result.metadata.hospital_name}
                        </Typography>
                      </Grid>
                    )}
                    {result.metadata.bill_date && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">
                          Date
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {result.metadata.bill_date}
                        </Typography>
                      </Grid>
                    )}
                    {result.metadata.invoice_number && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">
                          Invoice Number
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {result.metadata.invoice_number}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            )}

            {/* Flagged Items */}
            {result.analysis.flagged_count > 0 && (
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="error">
                    ⚠️ Detected Issues ({result.analysis.flagged_count})
                  </Typography>
                  {result.analysis.flagged_items.map((item, index) => (
                    <Accordion key={index}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            width: "100%",
                          }}
                        >
                          <Chip
                            label={item.type}
                            color={
                              item.type === "duplicate" ? "warning" : "error"
                            }
                            size="small"
                          />
                          <Chip
                            label={(item.severity || "medium").toUpperCase()}
                            color={severityColor(item.severity)}
                            variant="outlined"
                            size="small"
                          />
                          <Chip
                            label={`Confidence: ${Math.round((item.confidence ?? 0) * 100)}%`}
                            variant="outlined"
                            size="small"
                          />
                          <Typography flex={1}>{item.description}</Typography>
                          <Typography fontWeight="bold" color="error">
                            ₹{item.potential_saving.toLocaleString("en-IN")}
                          </Typography>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" color="text.secondary">
                          {item.issue}
                        </Typography>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="body2">
                          <strong>Line IDs:</strong> {item.line_ids.join(", ")}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Amount Charged:</strong> ₹
                          {item.amount.toLocaleString("en-IN")}
                        </Typography>
                        {item.category && (
                          <Typography variant="body2">
                            <strong>Category:</strong> {item.category}
                          </Typography>
                        )}
                        {item.market_rate && (
                          <Typography variant="body2">
                            <strong>Market Rate:</strong> ₹
                            {item.market_rate.toLocaleString("en-IN")}
                          </Typography>
                        )}
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Line Items Table */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Line Items ({result.line_items.length})
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Status</TableCell>
                        <TableCell>Line #</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell align="right">Qty</TableCell>
                        <TableCell align="right">Amount</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {result.line_items.map((item) => (
                        <TableRow key={item.line_id}>
                          <TableCell>{getStatusIcon(item.line_id)}</TableCell>
                          <TableCell>{item.line_id}</TableCell>
                          <TableCell>{item.description}</TableCell>
                          <TableCell align="right">{item.quantity}</TableCell>
                          <TableCell align="right">
                            ₹{item.amount.toLocaleString("en-IN")}
                          </TableCell>
                        </TableRow>
                      ))}
                      <TableRow>
                        <TableCell colSpan={4} align="right">
                          <strong>Total</strong>
                        </TableCell>
                        <TableCell align="right">
                          <strong>
                            ₹
                            {result.analysis.computed_total.toLocaleString(
                              "en-IN",
                            )}
                          </strong>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>

            {/* Recommendations */}
            {result.analysis.potential_savings > 0 && (
              <Alert severity="success" sx={{ mt: 3 }}>
                <Typography variant="body1" fontWeight="bold" gutterBottom>
                  💡 Potential Savings: ₹
                  {result.analysis.potential_savings.toLocaleString("en-IN")}
                </Typography>
                <Typography variant="body2">
                  We've identified potential overcharges and duplicates. You may
                  be able to contest these charges with your hospital or
                  insurance provider for reimbursement.
                </Typography>
              </Alert>
            )}
          </>
        )}
      </Container>

      {/* Chatbot Widget */}
      <ChatbotWidget pageContext="bill-buster" />
    </>
  );
};

export default BillBusterPage;
