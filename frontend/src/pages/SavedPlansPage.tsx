import React, { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Grid,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import Navigation from "../components/Navigation";
import { authAPI, insuranceAPI } from "../services/api";
import { SavedPlan } from "../types/insurance";

const SavedPlansPage: React.FC = () => {
  const navigate = useNavigate();
  const [savedPlans, setSavedPlans] = useState<SavedPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        if (!authAPI.isAuthenticated()) {
          setError("Please login to view saved plans.");
          return;
        }
        const plans = await insuranceAPI.getSavedPlans();
        setSavedPlans(plans || []);
      } catch (e: any) {
        setError(e.message || "Failed to load saved plans");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  return (
    <>
      <Navigation />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Typography variant="h4" fontWeight="bold">
            Saved Plans
          </Typography>
          <Button variant="outlined" onClick={() => navigate("/get-quote")}>
            Get New Quote
          </Button>
        </Box>

        {loading && <Typography>Loading saved plans...</Typography>}
        {error && (
          <Alert
            severity="warning"
            action={
              !authAPI.isAuthenticated() ? (
                <Button
                  color="inherit"
                  size="small"
                  onClick={() => navigate("/login")}
                >
                  Login
                </Button>
              ) : undefined
            }
          >
            {error}
          </Alert>
        )}

        {!loading && !error && savedPlans.length === 0 && (
          <Alert severity="info">
            No saved plans yet. Save a plan from recommendations.
          </Alert>
        )}

        <Grid container spacing={2}>
          {savedPlans.map((plan) => (
            <Grid item xs={12} md={6} lg={4} key={plan.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" fontWeight="bold">
                    {plan.plan_name}
                  </Typography>
                  <Typography color="text.secondary">
                    {plan.provider}
                  </Typography>
                  <Typography sx={{ mt: 1 }}>
                    <strong>Premium:</strong> ₹
                    {plan.premium.toLocaleString("en-IN")}
                  </Typography>
                  <Typography>
                    <strong>Coverage:</strong> ₹
                    {plan.coverage_amount.toLocaleString("en-IN")}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Saved on {new Date(plan.saved_at).toLocaleString()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </>
  );
};

export default SavedPlansPage;
