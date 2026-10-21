import React, { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Grid,
  Stack,
  Typography,
} from "@mui/material";
import ArrowBack from "@mui/icons-material/ArrowBack";
import Navigation from "../components/Navigation";
import { insuranceAPI } from "../services/api";
import { PlanRecommendation } from "../types/insurance";

const PlanDetailsPage: React.FC = () => {
  const { planId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [plan, setPlan] = useState<PlanRecommendation | null>(
    (location.state as any)?.plan || null,
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      if (plan || !planId) return;
      setLoading(true);
      setError(null);
      try {
        const response = await insuranceAPI.getPlanDetails(planId);
        if (response?.plan) {
          setPlan(response.plan);
        } else {
          setError("Plan not found");
        }
      } catch (e: any) {
        setError(e.message || "Failed to fetch plan details");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [plan, planId]);

  const handleSave = async () => {
    if (!plan) return;
    try {
      await insuranceAPI.savePlan({
        plan_id: plan.plan_id,
        plan_name: plan.plan_name,
        provider: plan.provider,
        premium: plan.premium,
        coverage_amount: plan.coverage_amount,
      });
      alert("Plan saved successfully");
    } catch (e: any) {
      alert(e.message || "Failed to save plan");
    }
  };

  return (
    <>
      <Navigation />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate(-1)}
          sx={{ mb: 2 }}
        >
          Back
        </Button>

        {loading && (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <CircularProgress />
          </Box>
        )}

        {error && <Alert severity="error">{error}</Alert>}

        {plan && (
          <Card>
            <CardContent>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                {plan.plan_name}
              </Typography>
              <Typography color="text.secondary" gutterBottom>
                {plan.provider}
              </Typography>

              <Stack
                direction="row"
                spacing={1}
                sx={{ my: 2, flexWrap: "wrap" }}
              >
                <Chip label={`Rank #${plan.rank}`} color="primary" />
                <Chip
                  label={`Confidence ${(plan.confidence * 100).toFixed(0)}%`}
                  color="success"
                />
                <Chip label={plan.plan_category || "Health Plan"} />
              </Stack>

              <Grid container spacing={2} sx={{ my: 1 }}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Annual Premium
                  </Typography>
                  <Typography variant="h6">
                    ₹{plan.premium.toLocaleString("en-IN")}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Monthly Premium
                  </Typography>
                  <Typography variant="h6">
                    ₹{plan.monthly_premium.toLocaleString("en-IN")}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Coverage Amount
                  </Typography>
                  <Typography variant="h6">
                    ₹{plan.coverage_amount.toLocaleString("en-IN")}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Network Hospitals
                  </Typography>
                  <Typography variant="h6">
                    {plan.network_size.toLocaleString("en-IN")}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Deductible
                  </Typography>
                  <Typography variant="h6">
                    ₹{plan.deductible.toLocaleString("en-IN")}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Co-pay
                  </Typography>
                  <Typography variant="h6">{plan.copay}%</Typography>
                </Grid>
              </Grid>

              <Typography variant="h6" sx={{ mt: 3 }}>
                Why this plan
              </Typography>
              <ul>
                {plan.bullets?.map((b, i) => (
                  <li key={i}>
                    <Typography variant="body2">{b}</Typography>
                  </li>
                ))}
              </ul>

              <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
                <Button variant="contained" onClick={handleSave}>
                  Save Plan
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => navigate("/saved-plans")}
                >
                  View Saved Plans
                </Button>
              </Stack>
            </CardContent>
          </Card>
        )}
      </Container>
    </>
  );
};

export default PlanDetailsPage;
