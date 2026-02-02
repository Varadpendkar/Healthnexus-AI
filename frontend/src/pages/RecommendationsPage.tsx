import React, { useState } from "react";
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
  Skeleton,
} from "@mui/material";
import { ArrowBack, Psychology, CheckCircle } from "@mui/icons-material";
import { PlanCard } from "../components/PlanCard";
import { ApiResponse } from "../types/insurance";
import Navigation from "../components/Navigation";

export const RecommendationsPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [selectedForComparison, setSelectedForComparison] = useState<string[]>(
    [],
  );

  const state = location.state as {
    results: ApiResponse;
    userProfile: any;
  } | null;

  if (!state || !state.results) {
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

  const { results, userProfile } = state;
  const { recommendations, user_profile, total_plans_evaluated } = results;

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
