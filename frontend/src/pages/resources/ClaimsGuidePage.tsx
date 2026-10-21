import React from "react";
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import ArrowBack from "@mui/icons-material/ArrowBack";
import LocalHospital from "@mui/icons-material/LocalHospital";
import Navigation from "../../components/Navigation";

const ClaimsGuidePage: React.FC = () => {
  const navigate = useNavigate();

  const cashlessSteps = [
    {
      label: "Get Admitted to Network Hospital",
      description:
        "Choose a hospital from your insurer's network. Carry your health card and valid ID proof.",
    },
    {
      label: "Fill Pre-Authorization Form",
      description:
        "At the insurance desk, fill out the pre-authorization form. Hospital staff will help you with this process.",
    },
    {
      label: "Submit Required Documents",
      description:
        "Provide your health card, policy details, ID proof, and doctor's prescription/admission note.",
    },
    {
      label: "Insurer Reviews Request",
      description:
        "The insurance company reviews your request (usually within 2-6 hours for emergencies).",
    },
    {
      label: "Approval & Treatment",
      description:
        "Once approved, treatment proceeds. The hospital bills the insurance company directly for covered expenses.",
    },
    {
      label: "Settle Excluded Charges",
      description:
        "Pay only for non-covered items like room upgrade charges, special diet, or items outside policy coverage.",
    },
  ];

  const reimbursementSteps = [
    {
      label: "Pay Hospital Bills",
      description:
        "Pay the full bill at the hospital and collect all original bills, receipts, and discharge summary.",
    },
    {
      label: "Collect Required Documents",
      description:
        "Gather all necessary documents: bills, prescriptions, diagnostic reports, discharge card, doctor's statement.",
    },
    {
      label: "Fill Claim Form",
      description:
        "Download and fill the claim form from your insurer's website or get it from their office.",
    },
    {
      label: "Submit Claim",
      description:
        "Submit the form with all documents to your insurance company within the specified time (usually 15-30 days).",
    },
    {
      label: "Insurer Processes Claim",
      description:
        "The company verifies documents and may request additional information. Processing typically takes 7-30 days.",
    },
    {
      label: "Receive Reimbursement",
      description:
        "Once approved, the reimbursement is transferred to your registered bank account.",
    },
  ];

  const documents = [
    "Duly filled and signed claim form",
    "Original hospital bills and receipts",
    "Discharge summary/card",
    "Doctor's prescriptions and consultation notes",
    "Diagnostic test reports (blood tests, X-rays, MRI, etc.)",
    "Pharmacy bills for medicines",
    "Photo ID proof (Aadhaar, PAN, Driving License)",
    "Bank account details for reimbursement",
    "Policy document copy",
    "For accidents: FIR copy (if applicable)",
    "Death certificate (in case of death claims)",
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
              <LocalHospital sx={{ fontSize: 40, color: "#10b981", mr: 2 }} />
              <Typography
                variant="h3"
                component="h1"
                sx={{ color: "#1e40af", fontWeight: 700 }}
              >
                Health Insurance Claims Guide
              </Typography>
            </Box>

            <Typography variant="body1" color="text.secondary" paragraph>
              Step-by-step guide on how to file and track your health insurance
              claims successfully.
            </Typography>

            <Alert severity="info" sx={{ my: 3 }}>
              <Typography variant="body2">
                <strong>Two types of claims:</strong> Cashless (hospital bills
                insurer directly) and Reimbursement (you pay first, then claim).
              </Typography>
            </Alert>

            <Box sx={{ my: 4 }}>
              <Typography
                variant="h5"
                gutterBottom
                sx={{ color: "#1e40af", fontWeight: 600, mb: 3 }}
              >
                🏥 Cashless Claim Process
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                paragraph
                sx={{ mb: 3 }}
              >
                Available only at network hospitals. The hospital settles bills
                directly with your insurer.
              </Typography>

              <Stepper orientation="vertical">
                {cashlessSteps.map((step, index) => (
                  <Step key={index} active={true}>
                    <StepLabel>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {step.label}
                      </Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ lineHeight: 1.7 }}
                      >
                        {step.description}
                      </Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </Box>

            <Box sx={{ my: 4 }}>
              <Typography
                variant="h5"
                gutterBottom
                sx={{ color: "#1e40af", fontWeight: 600, mb: 3 }}
              >
                💰 Reimbursement Claim Process
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                paragraph
                sx={{ mb: 3 }}
              >
                For non-network hospitals or when cashless facility isn't
                available. You pay upfront and claim later.
              </Typography>

              <Stepper orientation="vertical">
                {reimbursementSteps.map((step, index) => (
                  <Step key={index} active={true}>
                    <StepLabel>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {step.label}
                      </Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ lineHeight: 1.7 }}
                      >
                        {step.description}
                      </Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </Box>

            <Box sx={{ my: 4, p: 3, bgcolor: "#fef3c7", borderRadius: 2 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ color: "#92400e", fontWeight: 600 }}
              >
                📋 Documents Required for Claims
              </Typography>
              <Box component="ul" sx={{ pl: 3 }}>
                {documents.map((doc, index) => (
                  <li key={index}>
                    <Typography variant="body2" sx={{ mb: 0.5 }}>
                      {doc}
                    </Typography>
                  </li>
                ))}
              </Box>
            </Box>

            <Box sx={{ my: 4, p: 3, bgcolor: "#fee2e2", borderRadius: 2 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ color: "#991b1b", fontWeight: 600 }}
              >
                ⚠️ Common Reasons for Claim Rejection
              </Typography>
              <Box component="ul" sx={{ pl: 3, mb: 0 }}>
                <li>
                  <Typography variant="body2" paragraph>
                    Incomplete or incorrect documentation
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    Treatment during waiting period
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    Pre-existing condition not disclosed
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    Treatment not covered under policy
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    Delay in filing claim beyond permissible time
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2">
                    Treatment at non-network hospital without prior approval
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
                ✅ Tips for Smooth Claim Settlement
              </Typography>
              <Box component="ul" sx={{ pl: 3, mb: 0 }}>
                <li>
                  <Typography variant="body2" paragraph>
                    Keep all original bills, receipts, and reports safe
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    Inform your insurer immediately upon hospitalization
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    Get pre-authorization for planned treatments
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    Verify your policy coverage before treatment
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    Submit complete documentation on time
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" paragraph>
                    Keep copies of all submitted documents
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2">
                    Follow up regularly on claim status
                  </Typography>
                </li>
              </Box>
            </Box>

            <Box sx={{ mt: 5, p: 3, bgcolor: "#eff6ff", borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ color: "#1e40af" }}>
                💡 Choose Plans with High Claim Settlement Ratio
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Our recommendations include insurers with 95%+ claim settlement
                ratios for hassle-free claims.
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
                Find Reliable Insurance Plans
              </Button>
            </Box>
          </Paper>
        </Container>
      </Box>
    </>
  );
};

export default ClaimsGuidePage;
