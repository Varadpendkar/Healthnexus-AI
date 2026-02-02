import React from "react";
import {
  TextField,
  MenuItem,
  Grid,
  Typography,
  Slider,
  Box,
} from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";

const coverageOptions = [
  { value: 300000, label: "₹3 Lakh" },
  { value: 500000, label: "₹5 Lakh" },
  { value: 1000000, label: "₹10 Lakh" },
  { value: 2000000, label: "₹20 Lakh" },
  { value: 5000000, label: "₹50 Lakh" },
];

export const PreferencesStep: React.FC = () => {
  const { control, watch } = useFormContext();
  const budgetValue = watch("premium_budget", 5000);

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        Coverage Preferences
      </Typography>
      <Typography
        variant="body2"
        color="text.secondary"
        gutterBottom
        sx={{ mb: 3 }}
      >
        Specify your coverage requirements and budget
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Controller
            name="plan_type"
            control={control}
            rules={{ required: "Plan type is required" }}
            render={({ field }) => (
              <TextField {...field} select label="Plan Type *" fullWidth>
                <MenuItem value="individual">Individual</MenuItem>
                <MenuItem value="floater">Family Floater</MenuItem>
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Controller
            name="coverage_amount"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="Preferred Coverage Amount"
                fullWidth
              >
                {coverageOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Typography gutterBottom>
            Monthly Premium Budget: ₹{budgetValue?.toLocaleString("en-IN")}
          </Typography>
          <Controller
            name="premium_budget"
            control={control}
            render={({ field }) => (
              <Slider
                {...field}
                value={field.value || 5000}
                onChange={(_, value) => field.onChange(value)}
                min={1000}
                max={20000}
                step={500}
                marks={[
                  { value: 1000, label: "₹1k" },
                  { value: 10000, label: "₹10k" },
                  { value: 20000, label: "₹20k" },
                ]}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) =>
                  `₹${value.toLocaleString("en-IN")}`
                }
              />
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Controller
            name="preferred_providers"
            control={control}
            render={({ field: { onChange, value, ...field } }) => (
              <TextField
                {...field}
                value={value || ""}
                onChange={(e) =>
                  onChange(
                    e.target.value
                      ? e.target.value.split(",").map((s: string) => s.trim())
                      : [],
                  )
                }
                label="Preferred Insurance Providers (optional)"
                fullWidth
                placeholder="e.g., Star Health, HDFC Ergo, ICICI Lombard"
                helperText="Comma-separated list of preferred providers"
              />
            )}
          />
        </Grid>
      </Grid>
    </div>
  );
};
