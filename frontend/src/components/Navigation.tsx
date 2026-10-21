import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from "@mui/material";
import Login from "@mui/icons-material/Login";
import PersonAdd from "@mui/icons-material/PersonAdd";
import MenuBook from "@mui/icons-material/MenuBook";
import Receipt from "@mui/icons-material/Receipt";
import Favorite from "@mui/icons-material/Favorite";
import LocalHospital from "@mui/icons-material/LocalHospital";
import Logout from "@mui/icons-material/Logout";
import AutoAwesome from "@mui/icons-material/AutoAwesome";
import ArrowDropDown from "@mui/icons-material/ArrowDropDown";
import { authAPI } from "../services/api";

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(
    null,
  );
  const isAuthenticated = authAPI.isAuthenticated();
  const currentUser = authAPI.getCurrentUser();
  const displayName =
    currentUser?.username ||
    currentUser?.name ||
    currentUser?.email?.split("@")[0] ||
    "User";
  const userInitial = displayName.trim().charAt(0).toUpperCase();

  const handleLogout = () => {
    setUserMenuAnchor(null);
    authAPI.logout();
    navigate("/login");
  };

  const openUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const closeUserMenu = () => {
    setUserMenuAnchor(null);
  };

  const goTo = (path: string) => {
    closeUserMenu();
    navigate(path);
  };

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
          onClick={() => navigate("/bill-buster")}
          startIcon={<Receipt />}
        >
          Bill Buster
        </Button>
        <Button
          color="inherit"
          onClick={() => navigate("/smart-preauth")}
          startIcon={<LocalHospital />}
        >
          Smart Pre-Auth
        </Button>
        <Button
          color="inherit"
          onClick={() => navigate("/resources")}
          startIcon={<MenuBook />}
        >
          Resources
        </Button>
        <Button
          color="inherit"
          onClick={() => navigate("/saved-plans")}
          startIcon={<Favorite />}
        >
          Saved Plans
        </Button>
        {isAuthenticated ? (
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.25, ml: 2 }}>
            <Button
              onClick={openUserMenu}
              endIcon={<ArrowDropDown />}
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                px: 1.2,
                py: 0.6,
                borderRadius: 999,
                border: "1px solid",
                borderColor: "rgba(102, 126, 234, 0.3)",
                background:
                  "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
                color: "#4c1d95",
                textTransform: "none",
                minWidth: 0,
                "&:hover": {
                  background:
                    "linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)",
                },
              }}
            >
              <Avatar
                sx={{
                  width: 28,
                  height: 28,
                  fontSize: 14,
                  fontWeight: 700,
                  background:
                    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                }}
              >
                {userInitial}
              </Avatar>
              <Typography
                variant="body2"
                sx={{
                  fontWeight: 700,
                  color: "#4c1d95",
                  maxWidth: 140,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
                title={displayName}
              >
                {displayName}
              </Typography>
            </Button>

            <Menu
              anchorEl={userMenuAnchor}
              open={Boolean(userMenuAnchor)}
              onClose={closeUserMenu}
              PaperProps={{
                sx: {
                  mt: 1,
                  minWidth: 230,
                  borderRadius: 2,
                  border: "1px solid #e2e8f0",
                  boxShadow: "0 10px 30px rgba(2, 6, 23, 0.12)",
                },
              }}
            >
              <Box sx={{ px: 2, py: 1.2 }}>
                <Typography variant="caption" color="text.secondary">
                  Signed in as
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 700 }}>
                  {displayName}
                </Typography>
              </Box>
              <Divider />
              <MenuItem onClick={() => goTo("/get-quote")}>
                <ListItemIcon>
                  <AutoAwesome fontSize="small" />
                </ListItemIcon>
                <ListItemText primary="Get New Recommendation" />
              </MenuItem>
              <MenuItem onClick={() => goTo("/saved-plans")}>
                <ListItemIcon>
                  <Favorite fontSize="small" />
                </ListItemIcon>
                <ListItemText primary="My Saved Plans" />
              </MenuItem>
              <MenuItem onClick={() => goTo("/bill-buster")}>
                <ListItemIcon>
                  <Receipt fontSize="small" />
                </ListItemIcon>
                <ListItemText primary="Bill Buster" />
              </MenuItem>
              <MenuItem onClick={() => goTo("/smart-preauth")}>
                <ListItemIcon>
                  <LocalHospital fontSize="small" />
                </ListItemIcon>
                <ListItemText primary="Smart Pre-Auth" />
              </MenuItem>
              <MenuItem onClick={() => goTo("/resources")}>
                <ListItemIcon>
                  <MenuBook fontSize="small" />
                </ListItemIcon>
                <ListItemText primary="Resources Center" />
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <ListItemIcon>
                  <Logout fontSize="small" color="error" />
                </ListItemIcon>
                <ListItemText
                  primary="Logout"
                  primaryTypographyProps={{
                    color: "error.main",
                    fontWeight: 600,
                  }}
                />
              </MenuItem>
            </Menu>
          </Box>
        ) : (
          <>
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
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;
