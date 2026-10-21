import React from "react";
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Box,
  Divider,
  LinearProgress,
  Stack,
} from "@mui/material";
import CheckCircle from "@mui/icons-material/CheckCircle";
import LocalHospital from "@mui/icons-material/LocalHospital";
import AccountBalance from "@mui/icons-material/AccountBalance";
import Star from "@mui/icons-material/Star";
import BookmarkBorder from "@mui/icons-material/BookmarkBorder";
import BookmarkAdded from "@mui/icons-material/BookmarkAdded";
import { PlanRecommendation } from "../types/insurance";

interface Props {
  plan: PlanRecommendation;
  onViewDetails?: (planId: string) => void;
  onCompare?: (planId: string) => void;
  onSave?: (plan: PlanRecommendation) => void | Promise<void>;
  isSaved?: boolean;
  saveLoading?: boolean;
}

export const PlanCard: React.FC<Props> = ({
  plan,
  onViewDetails,
  onCompare,
  onSave,
  isSaved = false,
  saveLoading = false,
}) => {
  const isBestMatch = plan.rank === 1;
  const approvalRate = 100 - plan.claim_rejection_rate;

  return (
    <Card
      sx={{
        height: "100%",
        border: isBestMatch ? 3 : 1,
        borderColor: isBestMatch ? "success.main" : "divider",
        position: "relative",
        transition: "all 0.3s",
        "&:hover": {
          transform: "translateY(-8px)",
          boxShadow: 6,
        },
      }}
    >
      {isBestMatch && (
        <Chip
          icon={<Star />}
          label="Best Match"
          color="success"
          sx={{
            position: "absolute",
            top: 16,
            right: 16,
            fontWeight: "bold",
            zIndex: 1,
          }}
        />
      )}

      <CardContent>
        {/* Rank Badge */}
        <Box sx={{ display: "flex", alignItems: "flex-start", mb: 2 }}>
          <Chip
            label={`#${plan.rank}`}
            size="small"
            color="primary"
            sx={{ mr: 1 }}
          />
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              {plan.plan_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {plan.provider}
            </Typography>
          </Box>
        </Box>

        {/* Premium */}
        <Box
          sx={{
            my: 3,
            textAlign: "center",
            bgcolor: "primary.50",
            p: 2,
            borderRadius: 2,
          }}
        >
          <Typography variant="h3" color="primary.main" fontWeight="bold">
            ₹{plan.monthly_premium.toLocaleString("en-IN")}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            per month
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            ₹{plan.premium.toLocaleString("en-IN")} annually
          </Typography>
        </Box>

        {/* Key Features */}
        <Stack spacing={1.5} sx={{ mb: 2 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <AccountBalance fontSize="small" color="action" />
            <Typography variant="body2">
              <strong>Coverage:</strong> ₹
              {(plan.coverage_amount / 100000).toFixed(0)}L
            </Typography>
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <LocalHospital fontSize="small" color="action" />
            <Typography variant="body2">
              <strong>Network:</strong> {plan.network_size.toLocaleString()}{" "}
              hospitals
            </Typography>
          </Box>

          <Box>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}
            >
              <Typography variant="body2">
                <strong>Claim Approval:</strong>
              </Typography>
              <Typography
                variant="body2"
                color="success.main"
                fontWeight="bold"
              >
                {approvalRate.toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={approvalRate}
              color={
                approvalRate > 95
                  ? "success"
                  : approvalRate > 90
                    ? "primary"
                    : "warning"
              }
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>
        </Stack>

        <Divider sx={{ my: 2 }} />

        {/* AI Confidence */}
        <Box sx={{ mb: 2 }}>
          <Box
            sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}
          >
            <Typography variant="caption" color="text.secondary">
              AI Confidence Score
            </Typography>
            <Typography variant="caption" fontWeight="bold" color="primary">
              {(plan.confidence * 100).toFixed(0)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={plan.confidence * 100}
            sx={{ height: 6, borderRadius: 3 }}
          />
        </Box>

        {/* Why This Plan */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom fontWeight="bold">
            Why This Plan?
          </Typography>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {plan.bullets.slice(0, 3).map((bullet, idx) => (
              <li key={idx}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 0.5 }}
                >
                  {bullet}
                </Typography>
              </li>
            ))}
          </ul>
        </Box>

        {/* Conditions Considered */}
        {plan.conditions_considered &&
          plan.conditions_considered.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography
                variant="caption"
                color="info.main"
                sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
              >
                <CheckCircle fontSize="small" />
                Considers: {plan.conditions_considered.join(", ")}
              </Typography>
            </Box>
          )}

        {/* Premium Breakdown */}
        {plan.premium_breakdown && (
          <Box sx={{ mb: 2, p: 1.5, bgcolor: "grey.50", borderRadius: 1 }}>
            <Typography variant="caption" fontWeight="bold" gutterBottom>
              Premium Breakdown
            </Typography>
            <Stack spacing={0.5} sx={{ mt: 1 }}>
              <Box sx={{ display: "flex", justifyContent: "space-between" }}>
                <Typography variant="caption">Base Premium:</Typography>
                <Typography variant="caption">
                  ₹{plan.premium_breakdown.base.toLocaleString("en-IN")}
                </Typography>
              </Box>
              {plan.premium_breakdown.condition_loading > 0 && (
                <Box sx={{ display: "flex", justifyContent: "space-between" }}>
                  <Typography variant="caption" color="warning.main">
                    Condition Loading (+
                    {plan.premium_breakdown.condition_loading}%):
                  </Typography>
                  <Typography variant="caption" color="warning.main">
                    ₹
                    {(
                      plan.premium_breakdown.total - plan.premium_breakdown.base
                    ).toLocaleString("en-IN")}
                  </Typography>
                </Box>
              )}
            </Stack>
          </Box>
        )}

        {/* Action Buttons */}
        <Stack spacing={1}>
          <Stack direction="row" spacing={1}>
            <Button
              variant="contained"
              fullWidth
              onClick={() => onViewDetails?.(plan.plan_id)}
            >
              View Details
            </Button>
            <Button
              variant="outlined"
              onClick={() => onCompare?.(plan.plan_id)}
            >
              Compare
            </Button>
          </Stack>

          <Button
            variant={isSaved ? "contained" : "outlined"}
            color={isSaved ? "success" : "secondary"}
            fullWidth
            disabled={isSaved || saveLoading || !onSave}
            startIcon={isSaved ? <BookmarkAdded /> : <BookmarkBorder />}
            onClick={() => onSave?.(plan)}
          >
            {isSaved ? "Saved" : saveLoading ? "Saving..." : "Save Plan"}
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
};
