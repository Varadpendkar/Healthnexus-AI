import React from "react";
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import ArrowBack from "@mui/icons-material/ArrowBack";
import PlayCircleOutline from "@mui/icons-material/PlayCircleOutline";
import CheckCircle from "@mui/icons-material/CheckCircle";
import Cancel from "@mui/icons-material/Cancel";
import Navigation from "../../components/Navigation";

const TermVsWholeLifePage: React.FC = () => {
  const navigate = useNavigate();

  const comparison = [
    {
      aspect: "Coverage Duration",
      term: "Specific period (10, 20, 30 years)",
      whole: "Entire lifetime",
    },
    {
      aspect: "Premium",
      term: "Lower, affordable",
      whole: "Higher, more expensive",
    },
    {
      aspect: "Cash Value",
      term: "No cash value",
      whole: "Builds cash value over time",
    },
    {
      aspect: "Purpose",
      term: "Pure life protection",
      whole: "Protection + Investment",
    },
    {
      aspect: "Payout",
      term: "Death benefit only",
      whole: "Death benefit + Maturity benefit",
    },
    {
      aspect: "Best For",
      term: "Income replacement, debts",
      whole: "Estate planning, wealth building",
    },
  ];

  return (
    <>
      <Navigation />
      <Box sx={{ bgcolor: "#f8fafc", minHeight: "100vh", py: 8 }}>
        <Container maxWidth="md">
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate("/resources")}
            sx={{ mb: 3, color: "#667eea" }}
          >
            Back to Resources
          </Button>

          <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <PlayCircleOutline
                sx={{ fontSize: 40, color: "#f5576c", mr: 2 }}
              />
              <Typography
                variant="h3"
                component="h1"
                sx={{ color: "#1e40af", fontWeight: 700 }}
              >
                Term vs. Whole Life Insurance
              </Typography>
            </Box>

            <Typography variant="body1" color="text.secondary" paragraph>
              A comprehensive comparison of the two most popular types of life
              insurance to help you make the right choice.
            </Typography>

            <Grid container spacing={3} sx={{ my: 4 }}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, bgcolor: "#eff6ff", height: "100%" }}>
                  <Typography
                    variant="h5"
                    gutterBottom
                    sx={{ color: "#1e40af", fontWeight: 600 }}
                  >
                    📋 Term Life Insurance
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    paragraph
                    sx={{ lineHeight: 1.7 }}
                  >
                    Term life insurance provides coverage for a specific period.
                    If you pass away during the term, your beneficiaries receive
                    the death benefit. If you outlive the term, coverage ends
                    with no payout.
                  </Typography>
                  <Typography
                    variant="subtitle2"
                    gutterBottom
                    sx={{ mt: 2, fontWeight: 600 }}
                  >
                    Key Features:
                  </Typography>
                  <Box component="ul" sx={{ pl: 3 }}>
                    <li>
                      <Typography variant="body2">
                        Most affordable option
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        Simple and straightforward
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        High coverage at low cost
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        Renewable or convertible options
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        No cash value accumulation
                      </Typography>
                    </li>
                  </Box>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, bgcolor: "#fef3c7", height: "100%" }}>
                  <Typography
                    variant="h5"
                    gutterBottom
                    sx={{ color: "#92400e", fontWeight: 600 }}
                  >
                    💰 Whole Life Insurance
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    paragraph
                    sx={{ lineHeight: 1.7 }}
                  >
                    Whole life insurance (also called permanent insurance)
                    provides lifetime coverage. It includes a savings component
                    (cash value) that grows over time, which you can borrow
                    against or withdraw.
                  </Typography>
                  <Typography
                    variant="subtitle2"
                    gutterBottom
                    sx={{ mt: 2, fontWeight: 600 }}
                  >
                    Key Features:
                  </Typography>
                  <Box component="ul" sx={{ pl: 3 }}>
                    <li>
                      <Typography variant="body2">
                        Lifetime coverage guarantee
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        Builds cash value (tax-deferred)
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">Fixed premiums</Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        Can borrow against cash value
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        More expensive premiums
                      </Typography>
                    </li>
                  </Box>
                </Paper>
              </Grid>
            </Grid>

            <Typography
              variant="h5"
              gutterBottom
              sx={{ mt: 4, color: "#1e40af", fontWeight: 600 }}
            >
              Side-by-Side Comparison
            </Typography>

            <TableContainer component={Paper} sx={{ my: 3 }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: "#eff6ff" }}>
                    <TableCell sx={{ fontWeight: 600, width: "30%" }}>
                      Aspect
                    </TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Term Life</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Whole Life</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {comparison.map((row, index) => (
                    <TableRow key={index}>
                      <TableCell sx={{ fontWeight: 600 }}>
                        {row.aspect}
                      </TableCell>
                      <TableCell>{row.term}</TableCell>
                      <TableCell>{row.whole}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Grid container spacing={3} sx={{ my: 4 }}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, border: "2px solid #10b981" }}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <CheckCircle sx={{ color: "#10b981", mr: 1 }} />
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 600, color: "#065f46" }}
                    >
                      Choose Term Life If:
                    </Typography>
                  </Box>
                  <Box component="ul" sx={{ pl: 3, mb: 0 }}>
                    <li>
                      <Typography variant="body2" paragraph>
                        You need affordable, high coverage
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2" paragraph>
                        You want to cover specific debts (mortgage, education)
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2" paragraph>
                        You're young and need family protection
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2" paragraph>
                        You want simple, straightforward insurance
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        Your budget is limited
                      </Typography>
                    </li>
                  </Box>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, border: "2px solid #f59e0b" }}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <CheckCircle sx={{ color: "#f59e0b", mr: 1 }} />
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 600, color: "#92400e" }}
                    >
                      Choose Whole Life If:
                    </Typography>
                  </Box>
                  <Box component="ul" sx={{ pl: 3, mb: 0 }}>
                    <li>
                      <Typography variant="body2" paragraph>
                        You want lifelong coverage guaranteed
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2" paragraph>
                        You need estate planning tools
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2" paragraph>
                        You want to build tax-deferred savings
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2" paragraph>
                        You have dependents with special needs
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        You can afford higher premiums
                      </Typography>
                    </li>
                  </Box>
                </Paper>
              </Grid>
            </Grid>

            <Box sx={{ my: 4, p: 3, bgcolor: "#fee2e2", borderRadius: 2 }}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Cancel sx={{ color: "#dc2626", mr: 1 }} />
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 600, color: "#991b1b" }}
                >
                  Common Misconceptions
                </Typography>
              </Box>
              <Box component="ul" sx={{ pl: 3, mb: 0 }}>
                <li>
                  <Typography variant="body2" paragraph>
                    <strong>Myth:</strong> "Term insurance is a waste if I don't
                    die during the term."
                    <br />
                    <strong>Reality:</strong> It's like car insurance - you hope
                    you don't need it, but it provides critical protection when
                    you do.
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    <strong>Myth:</strong> "Whole life is always better because
                    it builds cash value."
                    <br />
                    <strong>Reality:</strong> The cash value growth is slow
                    initially and the higher premiums might prevent you from
                    getting adequate coverage.
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2">
                    <strong>Myth:</strong> "I can only have one or the other."
                    <br />
                    <strong>Reality:</strong> Many people combine both - term
                    for high coverage needs and whole life for permanent
                    protection.
                  </Typography>
                </li>
              </Box>
            </Box>

            <Box sx={{ my: 4, p: 3, bgcolor: "#d1fae5", borderRadius: 2 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ color: "#065f46", fontWeight: 600 }}
              >
                💡 Real Example
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Scenario:</strong> Raj, 30 years old, married with 2
                kids, needs ₹1 crore coverage
              </Typography>
              <Box component="ul" sx={{ pl: 3, mb: 0 }}>
                <li>
                  <Typography variant="body2" paragraph>
                    <strong>Term Plan Option:</strong> ₹12,000/year for 30 years
                    (Total: ₹3.6 lakhs)
                    <br />
                    Provides ₹1 crore coverage until age 60
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2">
                    <strong>Whole Life Option:</strong> ₹65,000/year for
                    lifetime (Total: ₹19.5 lakhs in 30 years)
                    <br />
                    Provides ₹1 crore coverage for life + builds cash value of
                    ~₹8-10 lakhs in 30 years
                  </Typography>
                </li>
              </Box>
            </Box>

            <Box sx={{ mt: 5, p: 3, bgcolor: "#eff6ff", borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ color: "#1e40af" }}>
                🎯 Not Sure Which is Right for You?
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                While this page focuses on life insurance, our platform
                specializes in health insurance. Get personalized
                recommendations based on your health needs and budget.
              </Typography>
              <Button
                variant="contained"
                onClick={() => navigate("/get-quote")}
                sx={{
                  background:
                    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "#ffffff",
                  "&:hover": {
                    background:
                      "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
                  },
                }}
              >
                Get Health Insurance Recommendations
              </Button>
            </Box>
          </Paper>
        </Container>
      </Box>
    </>
  );
};

export default TermVsWholeLifePage;
