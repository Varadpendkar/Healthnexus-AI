import React, { useState } from "react";
import { useForm, FormProvider } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import {
  Stepper,
  Step,
  StepLabel,
  Button,
  Box,
  Paper,
  Container,
  Typography,
  CircularProgress,
  Alert,
} from "@mui/material";
import { PersonalInfoStep } from "../components/GetQuote/PersonalInfoStep";
import { PreferencesStep } from "../components/GetQuote/PreferencesStep";
import { HealthStep } from "../components/GetQuote/HealthStep";
import { insuranceAPI } from "../services/api";
import { UserProfile } from "../types/insurance";
import Navigation from "../components/Navigation";

const steps = ["Personal Info", "Preferences", "Health Details"];

const defaultValues: Partial<UserProfile> = {
  plan_type: "individual",
  smoking_flag: false,
  dependents: 0,
  coverage_amount: 500000,
  premium_budget: 5000,
  claim_history_count: 0,
  renewal_loyalty_years: 0,
  has_diabetes: false,
  has_hypertension: false,
  has_heart_disease: false,
  has_asthma: false,
  has_obesity: false,
  has_thyroid: false,
};

export const GetQuotePage: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const methods = useForm<UserProfile>({
    defaultValues,
    mode: "onChange",
  });

  const onSubmit = async (data: UserProfile) => {
    setLoading(true);
    setError(null);

    try {
      console.log("Submitting user profile:", data);
      const response = await insuranceAPI.getRecommendations(data, 8);
      console.log("Received recommendations:", response);

      // Navigate to results page with data
      navigate("/recommendations", {
        state: {
          results: response,
          userProfile: data,
        },
      });
    } catch (err: any) {
      console.error("Error:", err);
      setError(
        err.message || "Failed to get recommendations. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    // Trigger validation for current step fields
    const fieldsToValidate = getFieldsForStep(activeStep);
    const isValid = await methods.trigger(fieldsToValidate);

    if (isValid) {
      if (activeStep === steps.length - 1) {
        // Last step - submit form
        methods.handleSubmit(onSubmit)();
      } else {
        setActiveStep((prev) => prev + 1);
      }
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const getFieldsForStep = (step: number): (keyof UserProfile)[] => {
    switch (step) {
      case 0:
        return [
          "age",
          "gender",
          "annual_income",
          "city",
          "state",
          "marital_status",
          "occupation_type",
        ];
      case 1:
        return ["plan_type"];
      case 2:
        return [];
      default:
        return [];
    }
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return <PersonalInfoStep />;
      case 1:
        return <PreferencesStep />;
      case 2:
        return <HealthStep />;
      default:
        return "Unknown step";
    }
  };

  return (
    <>
      <Navigation />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="h4"
              gutterBottom
              fontWeight="bold"
              color="primary"
            >
              Get Your Health Insurance Quote
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Answer a few questions to get AI-powered personalized
              recommendations
            </Typography>
          </Box>

          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {error && (
            <Alert
              severity="error"
              sx={{ mb: 3 }}
              onClose={() => setError(null)}
            >
              {error}
            </Alert>
          )}

          <FormProvider {...methods}>
            <form onSubmit={methods.handleSubmit(onSubmit)}>
              <Box sx={{ minHeight: 400 }}>{getStepContent(activeStep)}</Box>

              <Box
                sx={{ display: "flex", justifyContent: "space-between", mt: 4 }}
              >
                <Button
                  disabled={activeStep === 0 || loading}
                  onClick={handleBack}
                  variant="outlined"
                >
                  Back
                </Button>

                <Button
                  variant="contained"
                  onClick={handleNext}
                  disabled={loading}
                  startIcon={loading && <CircularProgress size={20} />}
                >
                  {loading
                    ? "Processing..."
                    : activeStep === steps.length - 1
                      ? "Get Recommendations"
                      : "Next"}
                </Button>
              </Box>
            </form>
          </FormProvider>
        </Paper>
      </Container>
    </>
  );
};
