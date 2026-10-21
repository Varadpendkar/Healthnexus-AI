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
  Card,
  CardContent,
  Container,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Stack,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { PersonalInfoStep } from "../components/GetQuote/PersonalInfoStep";
import { PreferencesStep } from "../components/GetQuote/PreferencesStep";
import { HealthStep } from "../components/GetQuote/HealthStep";
import { insuranceAPI } from "../services/api";
import {
  UserProfile,
  PatientReportProfile,
  PatientReportExtractionResponse,
} from "../types/insurance";
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

const recommendationFallbackValues: Pick<
  UserProfile,
  | "age"
  | "gender"
  | "annual_income"
  | "city"
  | "state"
  | "marital_status"
  | "occupation_type"
  | "plan_type"
> = {
  age: 35,
  gender: "male",
  annual_income: 600000,
  city: "Mumbai",
  state: "Maharashtra",
  marital_status: "single",
  occupation_type: "salaried",
  plan_type: "individual",
};

export const GetQuotePage: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reportFile, setReportFile] = useState<File | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);
  const [reportSummary, setReportSummary] =
    useState<PatientReportExtractionResponse | null>(null);
  const [defaultedFields, setDefaultedFields] = useState<string[]>([]);
  const navigate = useNavigate();

  const methods = useForm<UserProfile>({
    defaultValues,
    mode: "onChange",
  });

  const withRecommendationFallbacks = (profile: UserProfile): UserProfile => {
    const age = Number(profile.age);
    const annualIncome = Number(profile.annual_income);

    return {
      ...defaultValues,
      ...recommendationFallbackValues,
      ...profile,
      age: age > 0 ? age : recommendationFallbackValues.age,
      gender: profile.gender || recommendationFallbackValues.gender,
      annual_income:
        annualIncome > 0
          ? annualIncome
          : recommendationFallbackValues.annual_income,
      city: profile.city?.trim()
        ? profile.city
        : recommendationFallbackValues.city,
      state: profile.state?.trim()
        ? profile.state
        : recommendationFallbackValues.state,
      marital_status: profile.marital_status?.trim()
        ? profile.marital_status
        : recommendationFallbackValues.marital_status,
      occupation_type: profile.occupation_type?.trim()
        ? profile.occupation_type
        : recommendationFallbackValues.occupation_type,
      plan_type: profile.plan_type || recommendationFallbackValues.plan_type,
    } as UserProfile;
  };

  const applyFallbacksToForm = () => {
    const applied: string[] = [];

    const fallbackEntries: Array<[keyof UserProfile, string | number]> = [
      ["age", recommendationFallbackValues.age],
      ["gender", recommendationFallbackValues.gender],
      ["annual_income", recommendationFallbackValues.annual_income],
      ["city", recommendationFallbackValues.city],
      ["state", recommendationFallbackValues.state],
      ["marital_status", recommendationFallbackValues.marital_status],
      ["occupation_type", recommendationFallbackValues.occupation_type],
      ["plan_type", recommendationFallbackValues.plan_type],
    ];

    fallbackEntries.forEach(([field, fallbackValue]) => {
      const currentValue = methods.getValues(field);
      const missingString =
        typeof currentValue === "string" && currentValue.trim() === "";
      const missingNumber =
        typeof currentValue === "number" &&
        (Number.isNaN(currentValue) || currentValue <= 0);
      const isMissing =
        currentValue === undefined ||
        currentValue === null ||
        missingString ||
        missingNumber;

      if (isMissing) {
        methods.setValue(field, fallbackValue as never, {
          shouldDirty: true,
          shouldValidate: true,
        });
        applied.push(field);
      }
    });

    setDefaultedFields(applied);
  };

  const onSubmit = async (data: UserProfile) => {
    setLoading(true);
    setError(null);

    try {
      const submissionData = withRecommendationFallbacks(data);

      console.log("Submitting user profile:", submissionData);
      const response = await insuranceAPI.getRecommendations(submissionData, 8);
      console.log("Received recommendations:", response);

      // Navigate to results page with data
      navigate("/recommendations", {
        state: {
          results: response,
          userProfile: submissionData,
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

  const applyExtractedProfile = (profile: PatientReportProfile) => {
    if (typeof profile.age === "number" && profile.age > 0) {
      methods.setValue("age", profile.age, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    if (profile.gender) {
      methods.setValue("gender", profile.gender, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    if (
      typeof profile.annual_income === "number" &&
      profile.annual_income > 0
    ) {
      methods.setValue("annual_income", profile.annual_income, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    if (profile.city) {
      methods.setValue("city", profile.city, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    if (profile.state) {
      methods.setValue("state", profile.state, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    if (profile.marital_status) {
      methods.setValue("marital_status", profile.marital_status, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    if (profile.occupation_type) {
      methods.setValue("occupation_type", profile.occupation_type, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    if (typeof profile.dependents === "number" && profile.dependents >= 0) {
      methods.setValue("dependents", profile.dependents, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    if (typeof profile.smoking_flag === "boolean") {
      methods.setValue("smoking_flag", profile.smoking_flag, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    if (profile.plan_type) {
      methods.setValue("plan_type", profile.plan_type, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    methods.setValue("has_asthma", !!profile.conditions?.asthma, {
      shouldDirty: true,
    });
    methods.setValue("has_hypertension", !!profile.conditions?.hypertension, {
      shouldDirty: true,
    });
    methods.setValue("has_diabetes", !!profile.conditions?.diabetes, {
      shouldDirty: true,
    });
    methods.setValue("has_heart_disease", !!profile.conditions?.heart_disease, {
      shouldDirty: true,
    });
    methods.setValue("has_thyroid", !!profile.conditions?.thyroid, {
      shouldDirty: true,
    });
    methods.setValue("has_obesity", !!profile.conditions?.obesity, {
      shouldDirty: true,
    });
  };

  const handlePatientReportUpload = async () => {
    if (!reportFile) {
      setReportError("Please choose a report file first");
      return;
    }

    setReportLoading(true);
    setReportError(null);

    try {
      const response = await insuranceAPI.uploadPatientReport(reportFile);

      if (
        !response.success ||
        response.status === "error" ||
        !response.profile
      ) {
        throw new Error(response.error || "Failed to extract patient report");
      }

      applyExtractedProfile(response.profile);
      applyFallbacksToForm();
      setReportSummary(response);
    } catch (err: any) {
      setReportError(
        err?.response?.data?.error ||
          err?.message ||
          "Could not extract report details",
      );
    } finally {
      setReportLoading(false);
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

          <Card
            sx={{
              mb: 3,
              border: "1px dashed",
              borderColor: "primary.light",
              background:
                "linear-gradient(135deg, rgba(16,185,129,0.06) 0%, rgba(59,130,246,0.05) 100%)",
            }}
          >
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Upload Patient Report (Recommended)
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Upload a patient report (PDF/JPG/PNG/HEIC/TXT). We will
                auto-fill extracted details and complete missing required quote
                inputs with smart defaults.
              </Typography>

              <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
                <Button
                  component="label"
                  variant="outlined"
                  startIcon={<UploadFileIcon />}
                >
                  Choose Report
                  <input
                    hidden
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png,.heic,.txt"
                    onChange={(e) => {
                      const file = e.target.files?.[0] || null;
                      setReportFile(file);
                      setReportError(null);
                    }}
                  />
                </Button>

                <Button
                  variant="contained"
                  onClick={handlePatientReportUpload}
                  disabled={!reportFile || reportLoading}
                  startIcon={
                    reportLoading ? (
                      <CircularProgress size={16} color="inherit" />
                    ) : (
                      <UploadFileIcon />
                    )
                  }
                >
                  {reportLoading ? "Extracting..." : "Extract & Autofill"}
                </Button>
              </Stack>

              {reportFile && (
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ mt: 1, display: "block" }}
                >
                  Selected file: {reportFile.name}
                </Typography>
              )}

              {reportError && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {reportError}
                </Alert>
              )}

              {reportSummary?.success && reportSummary.profile && (
                <Box sx={{ mt: 2 }}>
                  <Alert severity="success" sx={{ mb: 1.5 }}>
                    Patient report extracted. We auto-filled report details and
                    applied defaults for missing required recommendation fields.
                    Please review before continuing.
                  </Alert>

                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {reportSummary.profile.name && (
                      <Chip
                        label={`Name: ${reportSummary.profile.name}`}
                        size="small"
                      />
                    )}
                    {reportSummary.profile.age && (
                      <Chip
                        label={`Age: ${reportSummary.profile.age}`}
                        size="small"
                      />
                    )}
                    {reportSummary.profile.city && (
                      <Chip
                        label={`City: ${reportSummary.profile.city}`}
                        size="small"
                      />
                    )}
                    {reportSummary.profile.state && (
                      <Chip
                        label={`State: ${reportSummary.profile.state}`}
                        size="small"
                      />
                    )}
                    {reportSummary.profile.conditions?.asthma && (
                      <Chip label="Asthma" color="warning" size="small" />
                    )}
                    {reportSummary.profile.conditions?.hypertension && (
                      <Chip label="Hypertension" color="warning" size="small" />
                    )}
                    {reportSummary.profile.conditions?.diabetes && (
                      <Chip label="Diabetes" color="warning" size="small" />
                    )}
                    {reportSummary.profile.conditions?.heart_disease && (
                      <Chip
                        label="Heart Disease"
                        color="warning"
                        size="small"
                      />
                    )}
                    {reportSummary.profile.conditions?.thyroid && (
                      <Chip label="Thyroid" color="warning" size="small" />
                    )}
                    {reportSummary.profile.conditions?.obesity && (
                      <Chip label="Obesity" color="warning" size="small" />
                    )}
                  </Stack>

                  {(reportSummary.missing_fields || []).length > 0 && (
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ mt: 1, display: "block" }}
                    >
                      Missing extracted fields:{" "}
                      {reportSummary.missing_fields?.join(", ")}
                    </Typography>
                  )}

                  {defaultedFields.length > 0 && (
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ mt: 0.5, display: "block" }}
                    >
                      Auto-filled with defaults: {defaultedFields.join(", ")}
                    </Typography>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>

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
