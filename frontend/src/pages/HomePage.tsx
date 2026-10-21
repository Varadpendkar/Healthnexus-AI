import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Box,
  Typography,
  Button,
  Grid,
  Paper,
  Card,
  CardContent,
} from "@mui/material";
import Psychology from "@mui/icons-material/Psychology";
import Speed from "@mui/icons-material/Speed";
import Security from "@mui/icons-material/Security";
import TrendingUp from "@mui/icons-material/TrendingUp";
import LocalHospital from "@mui/icons-material/LocalHospital";
import ArrowForward from "@mui/icons-material/ArrowForward";
import Navigation from "../components/Navigation";
import ChatbotWidget from "../components/ChatbotWidget";

const features = [
  {
    icon: <Psychology sx={{ fontSize: 48, color: "primary.main" }} />,
    title: "AI-Powered Recommendations",
    description:
      "LightGBM machine learning model analyzes thousands of plans to find your perfect match",
  },
  {
    icon: <Speed sx={{ fontSize: 48, color: "primary.main" }} />,
    title: "Instant Results",
    description:
      "Get personalized recommendations in seconds based on your health profile",
  },
  {
    icon: <Security sx={{ fontSize: 48, color: "primary.main" }} />,
    title: "Pre-existing Conditions",
    description:
      "Smart handling of diabetes, hypertension, heart disease with accurate premium calculation",
  },
  {
    icon: <LocalHospital sx={{ fontSize: 48, color: "primary.main" }} />,
    title: "Real Hospital Networks",
    description:
      "Access to 30+ top hospitals including Apollo, Fortis, Max, and AIIMS",
  },
];

export const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ bgcolor: "grey.50", minHeight: "100vh" }}>
      <Navigation />

      {/* Hero Section */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #10b981 0%, #047857 100%)",
          color: "white",
          py: 12,
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={7}>
              <Typography variant="h2" fontWeight="bold" gutterBottom>
                Healthnexus AI
              </Typography>
              <Typography variant="h5" sx={{ mb: 4, opacity: 0.95 }}>
                Find the Perfect Health Insurance Plan with AI
              </Typography>
              <Typography
                variant="body1"
                sx={{ mb: 4, fontSize: 18, opacity: 0.9 }}
              >
                Our machine learning model analyzes your health profile, budget,
                and preferences to recommend the best insurance plans tailored
                just for you.
              </Typography>
              <Box sx={{ display: "flex", gap: 2 }}>
                <Button
                  variant="contained"
                  size="large"
                  endIcon={<ArrowForward />}
                  onClick={() => navigate("/get-quote")}
                  sx={{
                    bgcolor: "white",
                    color: "primary.main",
                    "&:hover": {
                      bgcolor: "grey.100",
                    },
                    px: 4,
                    py: 1.5,
                    fontSize: 18,
                  }}
                >
                  Get Started
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  sx={{
                    borderColor: "white",
                    color: "white",
                    "&:hover": {
                      borderColor: "white",
                      bgcolor: "rgba(255, 255, 255, 0.1)",
                    },
                    px: 4,
                  }}
                >
                  Learn More
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={5}>
              <Box
                sx={{
                  bgcolor: "white",
                  borderRadius: 4,
                  p: 4,
                  boxShadow: 8,
                }}
              >
                <Typography
                  variant="h6"
                  color="primary.main"
                  fontWeight="bold"
                  gutterBottom
                >
                  Quick Stats
                </Typography>
                <Box sx={{ mt: 3 }}>
                  <Box sx={{ mb: 3 }}>
                    <Typography
                      variant="h3"
                      fontWeight="bold"
                      color="primary.main"
                    >
                      10,000+
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Insurance Plans Analyzed
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 3 }}>
                    <Typography
                      variant="h3"
                      fontWeight="bold"
                      color="primary.main"
                    >
                      30+
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Top Hospital Networks
                    </Typography>
                  </Box>
                  <Box>
                    <Typography
                      variant="h3"
                      fontWeight="bold"
                      color="primary.main"
                    >
                      95%+
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      AI Accuracy
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h4" align="center" fontWeight="bold" gutterBottom>
          Why Choose Healthnexus AI?
        </Typography>
        <Typography
          variant="body1"
          align="center"
          color="text.secondary"
          sx={{ mb: 6 }}
        >
          Powered by advanced machine learning for smarter insurance decisions
        </Typography>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  height: "100%",
                  transition: "transform 0.3s",
                  "&:hover": {
                    transform: "translateY(-8px)",
                    boxShadow: 6,
                  },
                }}
              >
                <CardContent sx={{ textAlign: "center", p: 3 }}>
                  <Box sx={{ mb: 2 }}>{feature.icon}</Box>
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box sx={{ bgcolor: "primary.50", py: 8 }}>
        <Container maxWidth="md">
          <Paper elevation={4} sx={{ p: 6, textAlign: "center" }}>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Ready to Find Your Perfect Plan?
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              Answer a few questions and get AI-powered recommendations in under
              3 minutes
            </Typography>
            <Button
              variant="contained"
              size="large"
              endIcon={<ArrowForward />}
              onClick={() => navigate("/get-quote")}
              sx={{ px: 6, py: 2, fontSize: 18 }}
            >
              Get Your Free Quote
            </Button>
          </Paper>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ bgcolor: "grey.900", color: "white", py: 4 }}>
        <Container maxWidth="lg">
          <Typography variant="body2" align="center">
            © 2026 Healthnexus AI. Powered by LightGBM ML Model.
          </Typography>
        </Container>
      </Box>

      {/* Chatbot Widget */}
      <ChatbotWidget pageContext="home" />
    </Box>
  );
};
