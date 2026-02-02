import React from "react";
import { TextField, MenuItem, Grid, Typography } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";

export const PersonalInfoStep: React.FC = () => {
  const {
    control,
    formState: { errors },
  } = useFormContext();

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        Personal Information
      </Typography>
      <Typography
        variant="body2"
        color="text.secondary"
        gutterBottom
        sx={{ mb: 3 }}
      >
        Tell us about yourself to get personalized recommendations
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Controller
            name="age"
            control={control}
            rules={{
              required: "Age is required",
              min: { value: 18, message: "Must be at least 18" },
              max: { value: 100, message: "Must be under 100" },
            }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Age *"
                type="number"
                fullWidth
                error={!!errors.age}
                helperText={errors.age?.message as string}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Controller
            name="gender"
            control={control}
            rules={{ required: "Gender is required" }}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="Gender *"
                fullWidth
                error={!!errors.gender}
                helperText={errors.gender?.message as string}
              >
                <MenuItem value="male">Male</MenuItem>
                <MenuItem value="female">Female</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Controller
            name="annual_income"
            control={control}
            rules={{
              required: "Annual income is required",
              min: { value: 100000, message: "Minimum ₹1,00,000" },
            }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Annual Income (₹) *"
                type="number"
                fullWidth
                error={!!errors.annual_income}
                helperText={errors.annual_income?.message as string}
                placeholder="e.g., 800000"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Controller
            name="city"
            control={control}
            rules={{ required: "City is required" }}
            render={({ field }) => (
              <TextField
                {...field}
                label="City *"
                fullWidth
                error={!!errors.city}
                helperText={errors.city?.message as string}
                placeholder="e.g., Mumbai"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Controller
            name="state"
            control={control}
            rules={{ required: "State is required" }}
            render={({ field }) => (
              <TextField
                {...field}
                label="State *"
                fullWidth
                error={!!errors.state}
                helperText={errors.state?.message as string}
                placeholder="e.g., Maharashtra"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Controller
            name="marital_status"
            control={control}
            rules={{ required: "Marital status is required" }}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="Marital Status *"
                fullWidth
                error={!!errors.marital_status}
                helperText={errors.marital_status?.message as string}
              >
                <MenuItem value="single">Single</MenuItem>
                <MenuItem value="married">Married</MenuItem>
                <MenuItem value="divorced">Divorced</MenuItem>
                <MenuItem value="widowed">Widowed</MenuItem>
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Controller
            name="dependents"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Number of Dependents"
                type="number"
                fullWidth
                helperText="Family members to be covered"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Controller
            name="occupation_type"
            control={control}
            rules={{ required: "Occupation type is required" }}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="Occupation Type *"
                fullWidth
                error={!!errors.occupation_type}
                helperText={errors.occupation_type?.message as string}
              >
                <MenuItem value="salaried">Salaried</MenuItem>
                <MenuItem value="self_employed">Self-Employed</MenuItem>
                <MenuItem value="student">Student</MenuItem>
                <MenuItem value="retired">Retired</MenuItem>
              </TextField>
            )}
          />
        </Grid>
      </Grid>
    </div>
  );
};
