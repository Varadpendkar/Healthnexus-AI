import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Container,
  Grid,
  Typography,
  Box,
  Paper,
  Button,
  Chip,
  Alert,
} from "@mui/material";
import { ArrowBack, Psychology, CheckCircle } from "@mui/icons-material";
import { PlanCard } from "../components/PlanCard";
import { ApiResponse } from "../types/insurance";
import Navigation from "../components/Navigation";
import { authAPI, insuranceAPI } from "../services/api";

export const RecommendationsPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [selectedForComparison, setSelectedForComparison] = useState<string[]>(
    [],
  );
  const [savedPlanIds, setSavedPlanIds] = useState<Set<string>>(new Set());
  const [savingPlanIds, setSavingPlanIds] = useState<Set<string>>(new Set());
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  const state = location.state as {
    results: ApiResponse;
    userProfile: any;
  } | null;

  const results = state?.results;
  const recommendations = results?.recommendations || [];
  const user_profile = results?.user_profile;
  const total_plans_evaluated = results?.total_plans_evaluated || 0;

  useEffect(() => {
    let mounted = true;

    const loadSaved = async () => {
      if (!results) return;
      if (!authAPI.isAuthenticated()) return;
      try {
        const savedPlans = await insuranceAPI.getSavedPlans();
        if (!mounted) return;
        setSavedPlanIds(new Set(savedPlans.map((p) => String(p.plan_id))));
      } catch (e: any) {
        if (!mounted) return;
        setSaveError(e.message || "Could not load saved plans");
      }
    };

    loadSaved();
    return () => {
      mounted = false;
    };
  }, [results]);

  if (!state || !results) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          No recommendations found. Please complete the quote form first.
        </Alert>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate("/get-quote")}
          sx={{ mt: 2 }}
        >
          Get Quote
        </Button>
      </Container>
    );
  }

  const handleCompare = (planId: string) => {
    setSelectedForComparison((prev) => {
      if (prev.includes(planId)) {
        return prev.filter((id) => id !== planId);
      }
      if (prev.length >= 3) {
        alert("You can compare maximum 3 plans");
        return prev;
      }
      return [...prev, planId];
    });
  };

  const handleViewDetails = (planId: string) => {
    navigate(`/plan/${planId}`, {
      state: { plan: recommendations.find((p) => p.plan_id === planId) },
    });
  };

  const handleSavePlan = async (plan: any) => {
    const planId = String(plan.plan_id);

    if (!authAPI.isAuthenticated()) {
      setSaveError("Please log in to save plans.");
      navigate("/login");
      return;
    }

    if (savedPlanIds.has(planId)) {
      setSaveSuccess("Plan already saved.");
      return;
    }

    setSaveError(null);
    setSaveSuccess(null);
    setSavingPlanIds((prev) => {
      const next = new Set(prev);
      next.add(planId);
      return next;
    });

    try {
      await insuranceAPI.savePlan({
        plan_id: plan.plan_id,
        plan_name: plan.plan_name,
        provider: plan.provider,
        premium: plan.premium,
        coverage_amount: plan.coverage_amount,
      });

      setSavedPlanIds((prev) => {
        const next = new Set(prev);
        next.add(planId);
        return next;
      });
      setSaveSuccess(`Saved: ${plan.plan_name}`);
    } catch (e: any) {
      const message = e.message || "Failed to save plan";
      setSaveError(message);
      if (message.toLowerCase().includes("log in")) {
        navigate("/login");
      }
    } finally {
      setSavingPlanIds((prev) => {
        const next = new Set(prev);
        next.delete(planId);
        return next;
      });
    }
  };

  return (
    <>
      <Navigation />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate("/get-quote")}
            sx={{ mb: 2 }}
          >
            Back to Quote Form
          </Button>

          <Paper
            elevation={2}
            sx={{
              p: 3,
              bgcolor: "primary.50",
              borderLeft: 4,
              borderColor: "primary.main",
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
              <Psychology sx={{ fontSize: 40, color: "primary.main" }} />
              <Box>
                <Typography variant="h4" fontWeight="bold" color="primary.main">
                  Your AI-Powered Recommendations
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Based on your health profile and preferences
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", mt: 2 }}>
              {user_profile && (
                <>
                  <Chip
                    label={`Age: ${user_profile.age}`}
                    icon={<CheckCircle />}
                  />
                  <Chip label={`${user_profile.city}`} icon={<CheckCircle />} />
                  {user_profile.conditions &&
                    user_profile.conditions.length > 0 && (
                      <Chip
                        label={`Conditions: ${user_profile.conditions.join(", ")}`}
                        icon={<CheckCircle />}
                        color="warning"
                      />
                    )}
                </>
              )}
              <Chip
                label={`${total_plans_evaluated} plans analyzed`}
                color="success"
                icon={<Psychology />}
              />
            </Box>
          </Paper>
        </Box>

        {/* Results Stats */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Top {recommendations.length} Plans for You
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Ranked by AI based on affordability, coverage, network, and your
            health conditions
          </Typography>
        </Box>

        {saveError && (
          <Alert
            severity="warning"
            sx={{ mb: 2 }}
            onClose={() => setSaveError(null)}
          >
            {saveError}
          </Alert>
        )}

        {saveSuccess && (
          <Alert
            severity="success"
            sx={{ mb: 2 }}
            onClose={() => setSaveSuccess(null)}
          >
            {saveSuccess}
          </Alert>
        )}

        {/* Comparison Bar */}
        {selectedForComparison.length > 0 && (
          <Paper
            elevation={3}
            sx={{
              p: 2,
              mb: 3,
              bgcolor: "info.50",
              position: "sticky",
              top: 16,
              zIndex: 10,
            }}
          >
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Typography variant="body2">
                Selected for comparison: {selectedForComparison.length}/3
              </Typography>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setSelectedForComparison([])}
                >
                  Clear
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  disabled={selectedForComparison.length < 2}
                  onClick={() =>
                    navigate("/compare", {
                      state: {
                        planIds: selectedForComparison,
                        allPlans: recommendations,
                      },
                    })
                  }
                >
                  Compare Plans
                </Button>
              </Box>
            </Box>
          </Paper>
        )}

        {/* Plan Cards Grid */}
        <Grid container spacing={3}>
          {recommendations.map((plan) => (
            <Grid item xs={12} md={6} lg={4} key={plan.plan_id}>
              <PlanCard
                plan={plan}
                onViewDetails={handleViewDetails}
                onCompare={handleCompare}
                onSave={handleSavePlan}
                isSaved={savedPlanIds.has(String(plan.plan_id))}
                saveLoading={savingPlanIds.has(String(plan.plan_id))}
              />
            </Grid>
          ))}
        </Grid>

        {/* No Results */}
        {recommendations.length === 0 && (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <Typography variant="h6" color="text.secondary">
              No recommendations available
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Please try adjusting your preferences and try again
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate("/get-quote")}
              sx={{ mt: 3 }}
            >
              Try Again
            </Button>
          </Box>
        )}
      </Container>
    </>
  );
};
