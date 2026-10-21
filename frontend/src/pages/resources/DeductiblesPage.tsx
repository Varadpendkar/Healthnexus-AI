import React from "react";
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import ArrowBack from "@mui/icons-material/ArrowBack";
import Calculate from "@mui/icons-material/Calculate";
import Navigation from "../../components/Navigation";

const DeductiblesPage: React.FC = () => {
  const navigate = useNavigate();

  const exampleScenarios = [
    {
      scenario: "Low Deductible Plan",
      deductible: "₹10,000",
      premium: "₹15,000/year",
      hospital: "₹1,00,000",
      youPay: "₹10,000 + ₹18,000",
      insurance: "₹72,000",
      total: "₹28,000",
    },
    {
      scenario: "High Deductible Plan",
      deductible: "₹50,000",
      premium: "₹8,000/year",
      hospital: "₹1,00,000",
      youPay: "₹50,000 + ₹10,000",
      insurance: "₹40,000",
      total: "₹60,000",
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
              <Calculate sx={{ fontSize: 40, color: "#3b82f6", mr: 2 }} />
              <Typography
                variant="h3"
                component="h1"
                sx={{ color: "#1e40af", fontWeight: 700 }}
              >
                Understanding Deductibles
              </Typography>
            </Box>

            <Typography variant="body1" color="text.secondary" paragraph>
              Learn how deductibles work and how they impact your premium and
              out-of-pocket expenses.
            </Typography>

            <Box sx={{ my: 4 }}>
              <Typography
                variant="h5"
                gutterBottom
                sx={{ color: "#1e40af", fontWeight: 600 }}
              >
                What is a Deductible?
              </Typography>
              <Typography
                variant="body1"
                color="text.secondary"
                paragraph
                sx={{ lineHeight: 1.7 }}
              >
                A deductible is the amount you must pay out-of-pocket for
                covered healthcare services before your insurance plan starts to
                pay. For example, if your deductible is ₹25,000, you pay the
                first ₹25,000 of covered services yourself. After that, you
                typically pay only a co-payment or co-insurance, and your
                insurer pays the rest.
              </Typography>
            </Box>

            <Box sx={{ my: 4, p: 3, bgcolor: "#dbeafe", borderRadius: 2 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ color: "#1e40af", fontWeight: 600 }}
              >
                How Deductibles Work
              </Typography>
              <Box component="ol" sx={{ pl: 2 }}>
                <li>
                  <Typography
                    variant="body1"
                    paragraph
                    sx={{ lineHeight: 1.7 }}
                  >
                    <strong>You pay the deductible:</strong> When you receive
                    healthcare services, you pay the full cost until you reach
                    your deductible amount.
                  </Typography>
                </li>
                <li>
                  <Typography
                    variant="body1"
                    paragraph
                    sx={{ lineHeight: 1.7 }}
                  >
                    <strong>Cost sharing begins:</strong> After meeting your
                    deductible, you and your insurance share costs through
                    co-payments or co-insurance.
                  </Typography>
                </li>
                <li>
                  <Typography
                    variant="body1"
                    paragraph
                    sx={{ lineHeight: 1.7 }}
                  >
                    <strong>Out-of-pocket maximum:</strong> Once you reach this
                    limit, insurance pays 100% of covered services for the rest
                    of the year.
                  </Typography>
                </li>
                <li>
                  <Typography variant="body1" sx={{ lineHeight: 1.7 }}>
                    <strong>Annual reset:</strong> Deductibles reset each policy
                    year, usually on January 1st or your policy renewal date.
                  </Typography>
                </li>
              </Box>
            </Box>

            <Typography
              variant="h5"
              gutterBottom
              sx={{ mt: 4, color: "#1e40af", fontWeight: 600 }}
            >
              Deductible vs. Premium Trade-off
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              paragraph
              sx={{ lineHeight: 1.7 }}
            >
              Generally, plans with higher deductibles have lower monthly
              premiums, while plans with lower deductibles have higher premiums.
              Here's a comparison:
            </Typography>

            <TableContainer component={Paper} sx={{ my: 3 }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: "#eff6ff" }}>
                    <TableCell sx={{ fontWeight: 600 }}>Aspect</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>
                      Low Deductible
                    </TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>
                      High Deductible
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Monthly Premium</TableCell>
                    <TableCell sx={{ color: "#dc2626" }}>Higher</TableCell>
                    <TableCell sx={{ color: "#059669" }}>Lower</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Out-of-pocket before coverage</TableCell>
                    <TableCell sx={{ color: "#059669" }}>Lower</TableCell>
                    <TableCell sx={{ color: "#dc2626" }}>Higher</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Best for</TableCell>
                    <TableCell>Frequent healthcare users</TableCell>
                    <TableCell>Healthy individuals</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Example</TableCell>
                    <TableCell>₹5,000 - ₹15,000</TableCell>
                    <TableCell>₹25,000 - ₹50,000</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>

            <Typography
              variant="h5"
              gutterBottom
              sx={{ mt: 4, color: "#1e40af", fontWeight: 600 }}
            >
              Real-World Example
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              paragraph
              sx={{ lineHeight: 1.7, mb: 3 }}
            >
              Let's say you need a hospital treatment costing ₹1,00,000. Here's
              how different deductible plans would work:
            </Typography>

            <TableContainer component={Paper} sx={{ my: 3 }}>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ bgcolor: "#eff6ff" }}>
                    <TableCell sx={{ fontWeight: 600 }}>Plan Type</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Deductible</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>
                      Annual Premium
                    </TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>
                      Hospital Bill
                    </TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>You Pay</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>
                      Insurance Pays
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {exampleScenarios.map((row, index) => (
                    <TableRow key={index}>
                      <TableCell sx={{ fontWeight: 600 }}>
                        {row.scenario}
                      </TableCell>
                      <TableCell>{row.deductible}</TableCell>
                      <TableCell>{row.premium}</TableCell>
                      <TableCell>{row.hospital}</TableCell>
                      <TableCell sx={{ color: "#dc2626", fontWeight: 600 }}>
                        {row.youPay}
                      </TableCell>
                      <TableCell sx={{ color: "#059669", fontWeight: 600 }}>
                        {row.insurance}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Typography
              variant="caption"
              display="block"
              color="text.secondary"
              sx={{ mt: 1, mb: 4 }}
            >
              *Assuming 20% co-insurance after deductible is met
            </Typography>

            <Box sx={{ my: 4, p: 3, bgcolor: "#fef3c7", borderRadius: 2 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ color: "#92400e", fontWeight: 600 }}
              >
                💡 Choosing the Right Deductible
              </Typography>
              <Box component="ul" sx={{ pl: 2, mb: 0 }}>
                <li>
                  <Typography variant="body2" paragraph>
                    <strong>Choose a low deductible if:</strong> You expect to
                    use healthcare services frequently, have ongoing medical
                    conditions, or prefer predictable costs.
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    <strong>Choose a high deductible if:</strong> You're
                    generally healthy, can afford emergency expenses, and want
                    to save on monthly premiums.
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2">
                    <strong>Consider your emergency fund:</strong> Can you
                    afford to pay the full deductible if needed? Ensure you have
                    savings to cover it.
                  </Typography>
                </li>
              </Box>
            </Box>

            <Box sx={{ mt: 5, p: 3, bgcolor: "#eff6ff", borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ color: "#1e40af" }}>
                🎯 Find Your Perfect Balance
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Our AI tool analyzes your health profile, budget, and risk
                tolerance to recommend plans with the optimal premium-deductible
                balance.
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
                Compare Plans with Different Deductibles
              </Button>
            </Box>
          </Paper>
        </Container>
      </Box>
    </>
  );
};

export default DeductiblesPage;
