import React from "react";
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Alert,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { ArrowBack, Warning } from "@mui/icons-material";
import Navigation from "../../components/Navigation";

const Top5MistakesPage: React.FC = () => {
  const navigate = useNavigate();

  const mistakes = [
    {
      title: "1. Choosing the Lowest Premium Without Checking Coverage",
      problem:
        "Many people select insurance based solely on the lowest monthly premium, ignoring what the plan actually covers.",
      consequence:
        "You might end up with high out-of-pocket costs when you need care, or discover critical services aren't covered.",
      solution:
        "Compare total potential costs including deductibles, co-pays, and out-of-pocket maximums. A slightly higher premium might save you thousands in the long run.",
    },
    {
      title: "2. Not Disclosing Pre-existing Conditions",
      problem:
        "Failing to disclose existing health conditions or medical history when purchasing insurance.",
      consequence:
        "Claims can be rejected, and your policy may be cancelled. Insurance fraud can have legal consequences.",
      solution:
        "Always provide complete and honest information about your health. Many insurers now cover pre-existing conditions after a waiting period.",
    },
    {
      title: "3. Ignoring the Network of Hospitals",
      problem:
        "Not checking if your preferred hospitals and doctors are in the insurer's network.",
      consequence:
        "You may face significantly higher costs or have to switch healthcare providers. Emergency situations could lead to unexpected bills.",
      solution:
        "Verify your preferred hospitals are in-network. Check if there are quality network hospitals near your home and workplace.",
    },
    {
      title: "4. Underestimating Coverage Amount",
      problem:
        "Choosing insufficient sum insured based on current healthcare costs without considering medical inflation.",
      consequence:
        "Medical costs are rising 10-15% annually. A ₹3 lakh cover today may not be adequate for a major illness in a few years.",
      solution:
        "Choose at least ₹5-10 lakh coverage. Consider your age, lifestyle, family history, and city's healthcare costs. Top-up plans can increase coverage affordably.",
    },
    {
      title: "5. Not Reading the Policy Document",
      problem:
        "Relying only on the sales person's verbal promises without reading the actual policy terms and conditions.",
      consequence:
        "Surprises during claim settlement - discovering exclusions, waiting periods, sub-limits, or conditions you weren't aware of.",
      solution:
        "Read the policy document carefully, especially sections on exclusions, claim procedures, and renewal terms. Ask questions about anything unclear.",
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
              <Warning sx={{ fontSize: 40, color: "#ef4444", mr: 2 }} />
              <Typography
                variant="h3"
                component="h1"
                sx={{ color: "#1e40af", fontWeight: 700 }}
              >
                Top 5 Mistakes to Avoid
              </Typography>
            </Box>

            <Typography variant="body1" color="text.secondary" paragraph>
              Learn about common pitfalls when purchasing health insurance and
              how to avoid them.
            </Typography>

            <Alert severity="warning" sx={{ my: 3 }}>
              <Typography variant="body2">
                <strong>Did you know?</strong> According to industry data, over
                30% of insurance claims face delays or rejections due to
                mistakes that could have been easily avoided during the purchase
                process.
              </Typography>
            </Alert>

            {mistakes.map((mistake, index) => (
              <Box
                key={index}
                sx={{
                  mb: 4,
                  p: 3,
                  bgcolor: index % 2 === 0 ? "#ffffff" : "#fafafa",
                  borderRadius: 2,
                  border: "1px solid #e5e7eb",
                }}
              >
                <Typography
                  variant="h5"
                  sx={{ fontWeight: 600, color: "#dc2626", mb: 2 }}
                >
                  {mistake.title}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{ fontWeight: 600, color: "#1e293b", mb: 0.5 }}
                  >
                    ❌ The Problem:
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ lineHeight: 1.7 }}
                  >
                    {mistake.problem}
                  </Typography>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{ fontWeight: 600, color: "#1e293b", mb: 0.5 }}
                  >
                    ⚠️ The Consequence:
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ lineHeight: 1.7 }}
                  >
                    {mistake.consequence}
                  </Typography>
                </Box>

                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ fontWeight: 600, color: "#1e293b", mb: 0.5 }}
                  >
                    ✅ The Solution:
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{ color: "#059669", lineHeight: 1.7, fontWeight: 500 }}
                  >
                    {mistake.solution}
                  </Typography>
                </Box>
              </Box>
            ))}

            <Box sx={{ mt: 5, p: 3, bgcolor: "#eff6ff", borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ color: "#1e40af" }}>
                💡 Make an Informed Decision
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Our AI-powered tool helps you avoid these mistakes by analyzing
                your needs and recommending the most suitable plans with
                transparent information.
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
                Get Smart Recommendations
              </Button>
            </Box>
          </Paper>
        </Container>
      </Box>
    </>
  );
};

export default Top5MistakesPage;
