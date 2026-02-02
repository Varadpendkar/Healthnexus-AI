import React from "react";
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { ArrowBack, CheckCircle, PlayCircleOutline } from "@mui/icons-material";
import Navigation from "../../components/Navigation";

const ChooseHealthInsurancePage: React.FC = () => {
  const navigate = useNavigate();

  const keyFactors = [
    "Assess your health needs and family medical history",
    "Determine your budget for monthly premiums",
    "Check the network hospitals and healthcare providers",
    "Review coverage limits and exclusions",
    "Compare deductibles and out-of-pocket maximums",
    "Look for additional benefits like wellness programs",
    "Read customer reviews and claim settlement ratios",
    "Understand waiting periods for pre-existing conditions",
  ];

  const steps = [
    {
      title: "1. Evaluate Your Health Needs",
      content:
        "Consider your age, existing health conditions, family medical history, and anticipated healthcare needs. If you have chronic conditions like diabetes or hypertension, ensure the plan covers ongoing treatments and medications.",
    },
    {
      title: "2. Set Your Budget",
      content:
        "Determine how much you can afford to pay monthly for premiums and what you can manage for out-of-pocket expenses. Remember, lower premiums often mean higher deductibles.",
    },
    {
      title: "3. Check the Network",
      content:
        "Verify that your preferred doctors, hospitals, and specialists are in the plan's network. Out-of-network care typically costs significantly more and may not be covered at all.",
    },
    {
      title: "4. Compare Coverage Options",
      content:
        "Look at what services are covered including preventive care, emergency services, prescription drugs, mental health services, and maternity care. Check for any exclusions or limitations.",
    },
    {
      title: "5. Understand Costs Beyond Premiums",
      content:
        "Consider deductibles (what you pay before insurance kicks in), co-payments (fixed amounts per visit), co-insurance (percentage you pay after deductible), and out-of-pocket maximums.",
    },
    {
      title: "6. Review Additional Benefits",
      content:
        "Many plans offer extras like wellness programs, telemedicine, health coaching, gym memberships, or preventive care incentives. These can add significant value.",
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
                How to Choose Health Insurance
              </Typography>
            </Box>

            <Typography variant="body1" color="text.secondary" paragraph>
              A comprehensive guide breaking down the key factors to consider
              when buying a health plan.
            </Typography>

            <Box sx={{ my: 4, p: 3, bgcolor: "#fef3c7", borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ color: "#92400e" }}>
                🎯 Key Factors to Consider
              </Typography>
              <List>
                {keyFactors.map((factor, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemIcon>
                      <CheckCircle sx={{ color: "#f59e0b" }} />
                    </ListItemIcon>
                    <ListItemText primary={factor} />
                  </ListItem>
                ))}
              </List>
            </Box>

            <Typography
              variant="h5"
              gutterBottom
              sx={{ mt: 4, mb: 3, color: "#1e40af", fontWeight: 600 }}
            >
              Step-by-Step Guide
            </Typography>

            {steps.map((step, index) => (
              <Box key={index} sx={{ mb: 3 }}>
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 600, color: "#667eea", mb: 1 }}
                >
                  {step.title}
                </Typography>
                <Typography
                  variant="body1"
                  color="text.secondary"
                  sx={{ lineHeight: 1.7 }}
                >
                  {step.content}
                </Typography>
              </Box>
            ))}

            <Box sx={{ mt: 5, p: 3, bgcolor: "#eff6ff", borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ color: "#1e40af" }}>
                💡 Ready to Find Your Perfect Plan?
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Use our AI-powered recommendation tool to get personalized
                health insurance suggestions based on your needs.
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
                Get Personalized Recommendations
              </Button>
            </Box>
          </Paper>
        </Container>
      </Box>
    </>
  );
};

export default ChooseHealthInsurancePage;
