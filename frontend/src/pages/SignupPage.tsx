import React, { useState } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import {
  Container,
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Link,
  Alert,
  InputAdornment,
  IconButton,
  Grid,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  PersonAdd as SignupIcon,
} from "@mui/icons-material";
import { authAPI } from "../services/api";
import Navigation from "../components/Navigation";

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    // Validate password strength
    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters long");
      setLoading(false);
      return;
    }

    try {
      const response = await authAPI.register(
        formData.name,
        formData.email,
        formData.password,
      );

      if (response.access_token) {
        // Token already stored by authAPI
        navigate("/get-quote");
      }
    } catch (err: any) {
      setError(
        err.response?.data?.error ||
          err.response?.data?.message ||
          "Registration failed. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navigation />
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          bgcolor: "#f8fafc",
          py: 8,
        }}
      >
        <Container maxWidth="sm">
          <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
            <Box sx={{ textAlign: "center", mb: 3 }}>
              <SignupIcon sx={{ fontSize: 50, color: "#2563eb", mb: 1 }} />
              <Typography
                variant="h4"
                component="h1"
                gutterBottom
                sx={{ fontWeight: 700 }}
              >
                Create Account
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Join Healthnexus AI to get personalized insurance
                recommendations
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Full Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                margin="normal"
                autoComplete="name"
                autoFocus
              />

              <TextField
                fullWidth
                label="Email Address"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                margin="normal"
                autoComplete="email"
              />

              <TextField
                fullWidth
                label="Password"
                name="password"
                type={showPassword ? "text" : "password"}
                value={formData.password}
                onChange={handleChange}
                required
                margin="normal"
                autoComplete="new-password"
                helperText="At least 6 characters"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                label="Confirm Password"
                name="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                margin="normal"
                autoComplete="new-password"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() =>
                          setShowConfirmPassword(!showConfirmPassword)
                        }
                        edge="end"
                      >
                        {showConfirmPassword ? (
                          <VisibilityOff />
                        ) : (
                          <Visibility />
                        )}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{
                  mt: 3,
                  mb: 2,
                  bgcolor: "#2563eb",
                  "&:hover": { bgcolor: "#1e40af" },
                  py: 1.5,
                }}
              >
                {loading ? "Creating Account..." : "Sign Up"}
              </Button>

              <Box sx={{ textAlign: "center", mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Already have an account?{" "}
                  <Link
                    component={RouterLink}
                    to="/login"
                    sx={{
                      color: "#2563eb",
                      fontWeight: 600,
                      textDecoration: "none",
                    }}
                  >
                    Sign In
                  </Link>
                </Typography>
              </Box>
            </form>
          </Paper>
        </Container>
      </Box>
    </>
  );
};

export default SignupPage;
