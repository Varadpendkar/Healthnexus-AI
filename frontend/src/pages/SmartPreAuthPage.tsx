import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  TextField,
  Button,
  Card,
  CardContent,
  CardHeader,
  Grid,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  CircularProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import HelpIcon from "@mui/icons-material/Help";
import Navigation from "../components/Navigation";

interface SmartPreAuthResult {
  query: string;
  extracted_procedure: string | null;
  extracted_hospital: string | null;
  extraction_confidence: string;
  estimate: any;
  rag_context: any[];
  explanation: string;
  suggestions: string[];
}

interface Hospital {
  code: string;
  name: string;
}

interface Procedure {
  code: string;
  name: string;
}

interface RoomType {
  code: string;
  name: string;
}

interface Insurer {
  code: string;
  name: string;
  coverage_percentage: number;
  accepted_hospital_count: number;
}

export default function SmartPreAuthPage() {
  const [query, setQuery] = useState("");
  const [roomType, setRoomType] = useState("standard");
  const [insurer, setInsurer] = useState("hdfc_ergo");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SmartPreAuthResult | null>(null);
  const [error, setError] = useState("");
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [procedures, setProcedures] = useState<Procedure[]>([]);
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [insurers, setInsurers] = useState<Insurer[]>([]);
  const [topNetworkHospitals, setTopNetworkHospitals] = useState<Hospital[]>(
    [],
  );
  const [loadingLists, setLoadingLists] = useState(true);

  // Load available options on mount
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [hospRes, procRes, roomRes, insurerRes] = await Promise.all([
          fetch("http://127.0.0.1:5001/api/smart-preauth/hospitals"),
          fetch("http://127.0.0.1:5001/api/smart-preauth/procedures"),
          fetch("http://127.0.0.1:5001/api/smart-preauth/room-types"),
          fetch("http://127.0.0.1:5001/api/smart-preauth/insurers"),
        ]);

        const hospData = await hospRes.json();
        const procData = await procRes.json();
        const roomData = await roomRes.json();
        const insurerData = await insurerRes.json();

        if (hospData.hospitals) setHospitals(hospData.hospitals);
        if (procData.procedures) setProcedures(procData.procedures);
        if (roomData.room_types) setRoomTypes(roomData.room_types);
        if (insurerData.insurers) setInsurers(insurerData.insurers);
        if (insurerData.top_network_hospitals) {
          setTopNetworkHospitals(insurerData.top_network_hospitals);
        }

        if (insurerData.insurers?.length > 0) {
          setInsurer(insurerData.insurers[0].code);
        }
      } catch (err) {
        console.error("Failed to load options:", err);
      } finally {
        setLoadingLists(false);
      }
    };

    fetchOptions();
  }, []);

  const handleQuery = async () => {
    if (!query.trim()) {
      setError("Please enter a query");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:5001/api/smart-preauth/query",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query,
            room_type: roomType,
            insurer,
          }),
        },
      );

      const data = await response.json();

      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || "Failed to process query");
      }
    } catch (err) {
      setError(
        "Network error. Make sure the backend is running on http://127.0.0.1:5001",
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const exampleQueries = [
    "What is the cost of knee surgery at Apollo?",
    "How much for cataract surgery at Fortis?",
    "Cost of heart surgery at Max Healthcare",
    "Delivery at Narayana Health private room",
    "Hip replacement at AIIMS standard room",
    "What is the cost of knee replacement at Ruby Hall Pune?",
    "What is the cost of angioplasty at Sahyadri Hospital Pune?",
  ];

  return (
    <>
      <Navigation />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <h1>💡 Smart Pre-Authorization Estimator</h1>
          <p>
            Ask natural language questions about medical procedure costs. AI
            extracts procedure & hospital info, then calculates your estimated
            out-of-pocket cost.
          </p>
          <p style={{ marginTop: "6px", color: "#666", fontSize: "0.9rem" }}>
            Network loaded: {insurers.length} insurers • {hospitals.length}{" "}
            hospitals • {procedures.length} procedures
          </p>
        </Box>

        {/* Query Input Section */}
        <Card sx={{ mb: 4, boxShadow: 3 }}>
          <CardHeader title="Ask About Procedure Costs" />
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  placeholder="Example: What's the cost for knee surgery at Apollo with private room?"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      handleQuery();
                    }
                  }}
                />
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Room Type</InputLabel>
                  <Select
                    value={roomType}
                    label="Room Type"
                    onChange={(e) => setRoomType(e.target.value)}
                  >
                    {roomTypes.map((rt) => (
                      <MenuItem key={rt.code} value={rt.code}>
                        {rt.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Insurance Provider</InputLabel>
                  <Select
                    value={insurer}
                    label="Insurance Provider"
                    onChange={(e) => setInsurer(e.target.value)}
                  >
                    {insurers.map((ins) => (
                      <MenuItem key={ins.code} value={ins.code}>
                        {ins.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={12} md={6}>
                <Button
                  fullWidth
                  variant="contained"
                  color="primary"
                  size="large"
                  startIcon={<SendIcon />}
                  onClick={handleQuery}
                  disabled={loading || loadingLists}
                >
                  {loading
                    ? "Processing..."
                    : loadingLists
                      ? "Loading options..."
                      : "Ask AI"}
                </Button>
              </Grid>
            </Grid>

            {/* Example Queries */}
            <Box sx={{ mt: 3 }}>
              <p
                style={{
                  fontSize: "0.9rem",
                  marginBottom: "10px",
                  color: "#666",
                }}
              >
                💬 Try these examples:
              </p>
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                {exampleQueries.map((q, idx) => (
                  <Chip
                    key={idx}
                    label={q}
                    onClick={() => setQuery(q)}
                    variant="outlined"
                    size="small"
                    color="primary"
                  />
                ))}
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Error Message */}
        {error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Results */}
        {result && (
          <Grid container spacing={3}>
            {/* Extraction Result */}
            <Grid item xs={12}>
              <Card>
                <CardHeader title="🔍 Extracted Information" />
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Box>
                        <p style={{ fontWeight: 500, marginBottom: "5px" }}>
                          Procedure
                        </p>
                        <Chip
                          label={result.extracted_procedure || "Not identified"}
                          color={
                            result.extracted_procedure ? "success" : "default"
                          }
                        />
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Box>
                        <p style={{ fontWeight: 500, marginBottom: "5px" }}>
                          Hospital
                        </p>
                        <Chip
                          label={result.extracted_hospital || "Not identified"}
                          color={
                            result.extracted_hospital ? "success" : "default"
                          }
                        />
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <p style={{ fontSize: "0.85rem", color: "#888" }}>
                        Confidence: {result.extraction_confidence}
                      </p>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Estimate Result */}
            {result.estimate && (
              <Grid item xs={12}>
                <Card sx={{ backgroundColor: "#f5f5f5" }}>
                  <CardHeader
                    title="💰 Cost Estimate"
                    backgroundColor="#e3f2fd"
                  />
                  <CardContent>
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow sx={{ backgroundColor: "#e3f2fd" }}>
                            <TableCell>Item</TableCell>
                            <TableCell align="right">Amount</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          <TableRow>
                            <TableCell>Base Procedure Cost</TableCell>
                            <TableCell align="right">
                              ₹{result.estimate.base_cost?.toLocaleString()}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Market Range</TableCell>
                            <TableCell align="right">
                              ₹
                              {result.estimate.estimated_cost_min?.toLocaleString()}{" "}
                              - ₹
                              {result.estimate.estimated_cost_max?.toLocaleString()}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Hospital Multiplier</TableCell>
                            <TableCell align="right">
                              {result.estimate.hospital_multiplier?.toFixed(2)}x
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Room Type Multiplier</TableCell>
                            <TableCell align="right">
                              {result.estimate.room_multiplier?.toFixed(2)}x
                            </TableCell>
                          </TableRow>
                          <TableRow
                            sx={{
                              fontWeight: "bold",
                              backgroundColor: "#fff9c4",
                            }}
                          >
                            <TableCell>Total Estimated Cost</TableCell>
                            <TableCell align="right">
                              ₹
                              {result.estimate.total_estimated?.toLocaleString()}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Insurance Coverage</TableCell>
                            <TableCell align="right">
                              {result.estimate.coverage_percentage}%
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Room Rent / Day</TableCell>
                            <TableCell align="right">
                              ₹
                              {result.estimate.room_rent_per_day?.toLocaleString()}
                            </TableCell>
                          </TableRow>
                          <TableRow
                            sx={{
                              fontWeight: "bold",
                              backgroundColor: "#c8e6c9",
                            }}
                          >
                            <TableCell>Your Out-of-Pocket Cost</TableCell>
                            <TableCell align="right">
                              ₹{result.estimate.out_of_pocket?.toLocaleString()}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Explanation */}
            <Grid item xs={12}>
              <Card>
                <CardHeader title="📋 Detailed Explanation" />
                <CardContent>
                  <Box
                    sx={{
                      backgroundColor: "#f5f5f5",
                      p: 2,
                      borderRadius: 1,
                      fontFamily: "monospace",
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                    }}
                  >
                    {result.explanation}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Suggestions */}
            {result.suggestions && result.suggestions.length > 0 && (
              <Grid item xs={12}>
                <Card>
                  <CardHeader title="💡 Next Steps" />
                  <CardContent>
                    <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                      {result.suggestions.map((suggestion, idx) => (
                        <Chip
                          key={idx}
                          icon={<HelpIcon />}
                          label={suggestion}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* RAG Context */}
            {result.rag_context && result.rag_context.length > 0 && (
              <Grid item xs={12}>
                <Card>
                  <CardHeader title="📚 Knowledge Base Context" />
                  <CardContent>
                    {result.rag_context.map((ctx, idx) => (
                      <Box
                        key={idx}
                        sx={{ mb: 2, pb: 2, borderBottom: "1px solid #eee" }}
                      >
                        <p style={{ fontWeight: 500, margin: "5px 0" }}>
                          {ctx.title || ctx.source || `Source ${idx + 1}`}
                        </p>
                        <p
                          style={{
                            fontSize: "0.9rem",
                            color: "#666",
                            margin: "5px 0",
                          }}
                        >
                          {ctx.content || JSON.stringify(ctx).substring(0, 200)}
                        </p>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        )}

        {/* Info Section */}
        <Card
          sx={{
            mt: 4,
            backgroundColor: "#e3f2fd",
            border: "2px solid #1565c0",
          }}
        >
          <CardHeader
            title="ℹ️ How It Works"
            sx={{ backgroundColor: "#1565c0", color: "white", fontWeight: 700 }}
          />
          <CardContent>
            {/* Network Summary */}
            <Box
              sx={{
                mb: 3,
                p: 2,
                backgroundColor: "#bbdefb",
                borderRadius: 1,
                border: "1px solid #1565c0",
              }}
            >
              <p
                style={{
                  margin: 0,
                  fontWeight: 600,
                  color: "#0d47a1",
                  fontSize: "0.95rem",
                }}
              >
                🌐 Network Loaded: {insurers.length} insurers •{" "}
                {hospitals.length} hospitals • {procedures.length}+ procedures
              </p>
            </Box>

            <ol>
              <li>
                <strong>Ask a Question:</strong> Describe the medical procedure
                and hospital in natural language
              </li>
              <li>
                <strong>AI Extraction:</strong> AI identifies the procedure and
                hospital from your query
              </li>
              <li>
                <strong>Cost Estimation:</strong> System calculates based on:
                <ul>
                  <li>Base procedure cost</li>
                  <li>Hospital-specific pricing multiplier</li>
                  <li>Room type adjustment</li>
                  <li>Your insurance coverage percentage</li>
                  <li>Cashless acceptance by hospital-insurer network</li>
                </ul>
              </li>
              <li>
                <strong>Result:</strong> Get your estimated out-of-pocket cost
                breakdown
              </li>
            </ol>

            <Box sx={{ mt: 3 }}>
              {/* Top Insurers Section */}
              <Box sx={{ mb: 3 }}>
                <p
                  style={{
                    margin: "0 0 12px 0",
                    fontWeight: 700,
                    fontSize: "1.05rem",
                    color: "#1565c0",
                    borderBottom: "2px solid #1565c0",
                    paddingBottom: "8px",
                  }}
                >
                  🏥 Top Insurers by Hospital Acceptance
                </p>
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                  {insurers.slice(0, 8).map((ins) => (
                    <Chip
                      key={ins.code}
                      label={`${ins.name} (${ins.accepted_hospital_count} hospitals)`}
                      size="small"
                      variant="outlined"
                      color="primary"
                    />
                  ))}
                </Box>
              </Box>

              {/* Top Hospitals Section */}
              <Box sx={{ mb: 2 }}>
                <p
                  style={{
                    margin: "0 0 12px 0",
                    fontWeight: 700,
                    fontSize: "1.05rem",
                    color: "#1565c0",
                    borderBottom: "2px solid #1565c0",
                    paddingBottom: "8px",
                  }}
                >
                  🏨 Hospitals Accepting Most Insurers
                </p>
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                  {topNetworkHospitals.slice(0, 8).map((h) => (
                    <Chip
                      key={h.code}
                      label={h.name}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </>
  );
}
