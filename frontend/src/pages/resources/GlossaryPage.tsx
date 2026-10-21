import React from "react";
import {
  Container,
  Typography,
  Box,
  Paper,
  Divider,
  Button,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import ArrowBack from "@mui/icons-material/ArrowBack";
import Navigation from "../../components/Navigation";

const GlossaryPage: React.FC = () => {
  const navigate = useNavigate();

  const glossaryTerms = [
    {
      term: "Premium",
      definition:
        "The amount you pay for your health insurance every month, regardless of whether you use medical services.",
    },
    {
      term: "Deductible",
      definition:
        "The amount you must pay out-of-pocket for covered healthcare services before your insurance plan starts to pay.",
    },
    {
      term: "Co-payment (Co-pay)",
      definition:
        "A fixed amount you pay for a covered healthcare service, usually when you receive the service.",
    },
    {
      term: "Co-insurance",
      definition:
        "Your share of the costs of a covered healthcare service, calculated as a percentage (e.g., 20%) of the allowed amount for the service.",
    },
    {
      term: "Out-of-Pocket Maximum",
      definition:
        "The most you have to pay for covered services in a plan year. After you spend this amount, your insurance plan pays 100% of covered services.",
    },
    {
      term: "Network",
      definition:
        "The facilities, providers, and suppliers your health insurer has contracted with to provide healthcare services.",
    },
    {
      term: "Pre-existing Condition",
      definition:
        "A health problem you had before the date your new health coverage starts, such as diabetes, asthma, or heart disease.",
    },
    {
      term: "Claim",
      definition:
        "A request for payment that you or your healthcare provider submits to your health insurer when you get items or services you think are covered.",
    },
    {
      term: "Coverage",
      definition:
        "The health care services and medications covered by your insurance plan, including preventive care, emergency services, and prescription drugs.",
    },
    {
      term: "Exclusions",
      definition:
        "Healthcare services or supplies that your health insurance plan doesn't cover or pay for.",
    },
    {
      term: "In-Network",
      definition:
        "Healthcare providers or facilities that have a contract with your health insurer to provide services at pre-negotiated rates.",
    },
    {
      term: "Out-of-Network",
      definition:
        "Providers or healthcare facilities that don't have a contract with your health plan. You'll typically pay more for out-of-network care.",
    },
    {
      term: "Cashless Hospitalization",
      definition:
        "A facility where the insurance company settles the hospital bill directly, so you don't need to pay upfront.",
    },
    {
      term: "Sum Insured",
      definition:
        "The maximum amount that the insurance company will pay for your medical treatment in a policy year.",
    },
    {
      term: "Waiting Period",
      definition:
        "The time you must wait before your health insurance coverage begins or before certain benefits become available.",
    },
    {
      term: "Renewal",
      definition:
        "The process of continuing your health insurance policy for another term by paying the renewal premium before the policy expires.",
    },
    {
      term: "Rider",
      definition:
        "An add-on benefit that you can purchase to enhance your base health insurance policy, such as maternity cover or critical illness cover.",
    },
    {
      term: "No Claim Bonus (NCB)",
      definition:
        "A reward in the form of increased sum insured or reduced premium for not making any claims during the policy year.",
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
            <Typography
              variant="h3"
              component="h1"
              gutterBottom
              sx={{ color: "#1e40af", fontWeight: 700 }}
            >
              Insurance Glossary
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              A comprehensive A-Z guide to understanding common insurance terms
              and jargon.
            </Typography>

            <Divider sx={{ my: 3 }} />

            <Box sx={{ mt: 4 }}>
              {glossaryTerms.map((item, index) => (
                <Box key={index} sx={{ mb: 3 }}>
                  <Typography
                    variant="h6"
                    sx={{ fontWeight: 600, color: "#667eea", mb: 1 }}
                  >
                    {item.term}
                  </Typography>
                  <Typography
                    variant="body1"
                    color="text.secondary"
                    sx={{ lineHeight: 1.7 }}
                  >
                    {item.definition}
                  </Typography>
                </Box>
              ))}
            </Box>

            <Box sx={{ mt: 5, p: 3, bgcolor: "#eff6ff", borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ color: "#1e40af" }}>
                💡 Pro Tip
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Understanding these terms will help you make informed decisions
                when comparing insurance plans and reading policy documents.
                Always ask your insurance provider if you're unsure about any
                term.
              </Typography>
            </Box>
          </Paper>
        </Container>
      </Box>
    </>
  );
};

export default GlossaryPage;
