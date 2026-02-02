import React from "react";
import { useNavigate } from "react-router-dom";
import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import { Login, PersonAdd, MenuBook } from "@mui/icons-material";

const Navigation: React.FC = () => {
  const navigate = useNavigate();

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{ bgcolor: "white", color: "text.primary" }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          component="div"
          onClick={() => navigate("/")}
          sx={{
            flexGrow: 1,
            fontWeight: 700,
            color: "primary.main",
            cursor: "pointer",
          }}
        >
          Healthnexus AI
        </Typography>
        <Button
          color="inherit"
          onClick={() => navigate("/resources")}
          startIcon={<MenuBook />}
        >
          Resources
        </Button>
        <Button
          color="inherit"
          onClick={() => navigate("/login")}
          startIcon={<Login />}
        >
          Login
        </Button>
        <Button
          variant="contained"
          onClick={() => navigate("/signup")}
          startIcon={<PersonAdd />}
          sx={{ ml: 2 }}
        >
          Sign Up
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;
