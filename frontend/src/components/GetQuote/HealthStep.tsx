import React from "react";
import {
  FormControlLabel,
  Checkbox,
  Grid,
  Typography,
  TextField,
  MenuItem,
  Box,
  Chip,
} from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import WarningIcon from "@mui/icons-material/Warning";

const conditions = [
  { name: "has_diabetes", label: "Diabetes", icon: "🩸" },
  { name: "has_hypertension", label: "Hypertension (High BP)", icon: "❤️" },
  { name: "has_heart_disease", label: "Heart Disease", icon: "💔" },
  { name: "has_asthma", label: "Asthma", icon: "🫁" },
  { name: "has_obesity", label: "Obesity", icon: "⚖️" },
  { name: "has_thyroid", label: "Thyroid Disorder", icon: "🦋" },
];

export const HealthStep: React.FC = () => {
  const { control, watch } = useFormContext();
  const selectedConditions = conditions.filter((c) => watch(c.name));

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        Health Information
      </Typography>
      <Typography
        variant="body2"
        color="text.secondary"
        gutterBottom
        sx={{ mb: 3 }}
      >
        Accurate health information helps us recommend the right plans
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Controller
            name="smoking_flag"
            control={control}
            render={({ field: { value, onChange, ...field } }) => (
              <TextField
                {...field}
                select
                label="Smoking Status *"
                fullWidth
                value={value ? "true" : "false"}
                onChange={(e) => onChange(e.target.value === "true")}
              >
                <MenuItem value="false">Non-smoker</MenuItem>
                <MenuItem value="true">Smoker / Ex-smoker</MenuItem>
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Controller
            name="claim_history_count"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Previous Claims Count"
                type="number"
                fullWidth
                helperText="Number of insurance claims in last 3 years"
              />
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Box
            sx={{
              p: 2,
              bgcolor: "warning.light",
              borderRadius: 1,
              display: "flex",
              alignItems: "center",
              gap: 1,
              mb: 2,
            }}
          >
            <WarningIcon sx={{ color: "warning.dark" }} />
            <Typography variant="body2" color="warning.dark">
              <strong>Pre-existing Conditions:</strong> Select all that apply.
              This affects premium but ensures proper coverage.
            </Typography>
          </Box>

          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
            Pre-existing Health Conditions
          </Typography>

          <Grid container spacing={2}>
            {conditions.map((condition) => (
              <Grid item xs={12} sm={6} md={4} key={condition.name}>
                <Controller
                  name={condition.name}
                  control={control}
                  defaultValue={false}
                  render={({ field: { value, onChange, ...field } }) => (
                    <Box
                      sx={{
                        p: 1.5,
                        border: 1,
                        borderColor: value ? "primary.main" : "grey.300",
                        borderRadius: 1,
                        bgcolor: value ? "primary.50" : "transparent",
                        transition: "all 0.2s",
                        "&:hover": {
                          borderColor: "primary.main",
                          bgcolor: "primary.50",
                        },
                      }}
                    >
                      <FormControlLabel
                        control={
                          <Checkbox
                            {...field}
                            checked={value || false}
                            onChange={(e) => onChange(e.target.checked)}
                          />
                        }
                        label={
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                            }}
                          >
                            <span>{condition.icon}</span>
                            <Typography variant="body2">
                              {condition.label}
                            </Typography>
                          </Box>
                        }
                      />
                    </Box>
                  )}
                />
              </Grid>
            ))}
          </Grid>

          {selectedConditions.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Selected conditions:
              </Typography>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mt: 1 }}>
                {selectedConditions.map((condition) => (
                  <Chip
                    key={condition.name}
                    label={`${condition.icon} ${condition.label}`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}
        </Grid>

        <Grid item xs={12} md={6}>
          <Controller
            name="renewal_loyalty_years"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Years with Current Insurer"
                type="number"
                fullWidth
                helperText="For portability benefits (leave 0 if new)"
              />
            )}
          />
        </Grid>
      </Grid>
    </div>
  );
};
