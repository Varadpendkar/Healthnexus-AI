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
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Login as LoginIcon,
} from "@mui/icons-material";
import { authAPI } from "../services/api";
import Navigation from "../components/Navigation";

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
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

    try {
      const response = await authAPI.login(formData.email, formData.password);

      if (response.access_token) {
        // Token already stored by authAPI
        navigate("/get-quote");
      }
    } catch (err: any) {
      setError(
        err.response?.data?.error ||
          err.response?.data?.message ||
          "Login failed. Please check your credentials.",
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
              <LoginIcon sx={{ fontSize: 50, color: "#2563eb", mb: 1 }} />
              <Typography
                variant="h4"
                component="h1"
                gutterBottom
                sx={{ fontWeight: 700 }}
              >
                Welcome Back
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Sign in to access your Healthnexus AI account
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
                label="Email Address"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                margin="normal"
                autoComplete="email"
                autoFocus
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
                autoComplete="current-password"
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
                {loading ? "Signing In..." : "Sign In"}
              </Button>

              <Box sx={{ textAlign: "center", mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Don't have an account?{" "}
                  <Link
                    component={RouterLink}
                    to="/signup"
                    sx={{
                      color: "#2563eb",
                      fontWeight: 600,
                      textDecoration: "none",
                    }}
                  >
                    Sign Up
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

export default LoginPage;
