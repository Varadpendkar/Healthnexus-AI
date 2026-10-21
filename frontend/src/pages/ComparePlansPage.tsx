import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import Navigation from "../components/Navigation";
import { PlanRecommendation } from "../types/insurance";

const ComparePlansPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const state = location.state as {
    allPlans: PlanRecommendation[];
    planIds: string[];
  } | null;

  if (!state || !state.allPlans || !state.planIds || state.planIds.length < 2) {
    return (
      <>
        <Navigation />
        <Container sx={{ py: 4 }}>
          <Alert severity="warning">
            Please select at least 2 plans to compare.
          </Alert>
          <Button
            sx={{ mt: 2 }}
            variant="contained"
            onClick={() => navigate("/recommendations")}
          >
            Back to Recommendations
          </Button>
        </Container>
      </>
    );
  }

  const selected = state.allPlans.filter((p) =>
    state.planIds.includes(p.plan_id),
  );

  const rows: Array<{
    label: string;
    value: (p: PlanRecommendation) => React.ReactNode;
  }> = [
    { label: "Provider", value: (p) => p.provider },
    {
      label: "Monthly Premium",
      value: (p) => `₹${p.monthly_premium.toLocaleString("en-IN")}`,
    },
    {
      label: "Annual Premium",
      value: (p) => `₹${p.premium.toLocaleString("en-IN")}`,
    },
    {
      label: "Coverage",
      value: (p) => `₹${p.coverage_amount.toLocaleString("en-IN")}`,
    },
    {
      label: "Network Hospitals",
      value: (p) => p.network_size.toLocaleString("en-IN"),
    },
    {
      label: "Deductible",
      value: (p) => `₹${p.deductible.toLocaleString("en-IN")}`,
    },
    { label: "Co-pay", value: (p) => `${p.copay}%` },
    { label: "Claim Rejection", value: (p) => `${p.claim_rejection_rate}%` },
    {
      label: "AI Confidence",
      value: (p) => `${(p.confidence * 100).toFixed(0)}%`,
    },
  ];

  return (
    <>
      <Navigation />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Typography variant="h4" fontWeight="bold">
            Compare Plans
          </Typography>
          <Button variant="outlined" onClick={() => navigate(-1)}>
            Back
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>
                  <strong>Feature</strong>
                </TableCell>
                {selected.map((plan) => (
                  <TableCell key={plan.plan_id}>
                    <strong>{plan.plan_name}</strong>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.label}>
                  <TableCell>
                    <strong>{row.label}</strong>
                  </TableCell>
                  {selected.map((plan) => (
                    <TableCell key={`${plan.plan_id}-${row.label}`}>
                      {row.value(plan)}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
              <TableRow>
                <TableCell>
                  <strong>Actions</strong>
                </TableCell>
                {selected.map((plan) => (
                  <TableCell key={`${plan.plan_id}-action`}>
                    <Button
                      size="small"
                      variant="contained"
                      onClick={() =>
                        navigate(`/plan/${plan.plan_id}`, { state: { plan } })
                      }
                    >
                      View Details
                    </Button>
                  </TableCell>
                ))}
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Container>
    </>
  );
};

export default ComparePlansPage;
