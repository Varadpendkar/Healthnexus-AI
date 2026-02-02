import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Box,
  Paper,
  Chip,
} from "@mui/material";
import Navigation from "../components/Navigation";
import {
  MenuBook,
  VideoLibrary,
  Description,
  GetApp,
  School,
  LocalHospital,
  PlayCircleOutline,
  ArrowForward,
} from "@mui/icons-material";

interface Resource {
  title: string;
  type: string;
  description: string;
  icon: React.ReactNode;
  buttonText: string;
  disabled?: boolean;
  path?: string;
}

const ResourcesPage: React.FC = () => {
  const navigate = useNavigate();

  const resources: Resource[] = [
    {
      title: "Insurance Glossary",
      type: "Glossary",
      description:
        "Understand common insurance terms and jargon. A comprehensive A-Z guide.",
      icon: <MenuBook sx={{ fontSize: 40, color: "#ffffff" }} />,
      buttonText: "View Glossary",
      path: "/resources/glossary",
    },
    {
      title: "How to Choose Health Insurance",
      type: "Video",
      description:
        "An explainer video breaking down the key factors to consider when buying a health plan.",
      icon: <VideoLibrary sx={{ fontSize: 40, color: "#ffffff" }} />,
      buttonText: "Read Guide",
      path: "/resources/choose-health-insurance",
    },
    {
      title: "Top 5 Mistakes to Avoid",
      type: "Article",
      description:
        "An in-depth article on common pitfalls when purchasing life insurance.",
      icon: <Description sx={{ fontSize: 40, color: "#ffffff" }} />,
      buttonText: "Read Article",
      path: "/resources/top-5-mistakes",
    },
    {
      title: "Financial Planning Template",
      type: "Template",
      description:
        "Download our Excel template to help you assess your insurance needs and budget.",
      icon: <GetApp sx={{ fontSize: 40, color: "#ffffff" }} />,
      buttonText: "Download",
      disabled: true,
    },
    {
      title: "Understanding Deductibles",
      type: "Article",
      description:
        "Learn how deductibles work and how they impact your premium and out-of-pocket expenses.",
      icon: <School sx={{ fontSize: 40, color: "#ffffff" }} />,
      buttonText: "Read Guide",
      path: "/resources/understanding-deductibles",
    },
    {
      title: "Health Insurance Claims Guide",
      type: "Guide",
      description:
        "Step-by-step guide on how to file and track your health insurance claims successfully.",
      icon: <LocalHospital sx={{ fontSize: 40, color: "#ffffff" }} />,
      buttonText: "View Guide",
      path: "/resources/claims-guide",
    },
    {
      title: "Term vs. Whole Life Insurance",
      type: "Video",
      description:
        "A short video comparing the pros and cons of the two most popular types of life insurance.",
      icon: <PlayCircleOutline sx={{ fontSize: 40, color: "#ffffff" }} />,
      buttonText: "Read Comparison",
      path: "/resources/term-vs-whole-life",
    },
  ];

  const getGradientForType = (type: string) => {
    switch (type) {
      case "Video":
        return "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)";
      case "Article":
        return "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)";
      case "Template":
        return "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)";
      case "Guide":
        return "linear-gradient(135deg, #fa709a 0%, #fee140 100%)";
      case "Glossary":
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)";
      default:
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)";
    }
  };

  const getChipColors = (type: string) => {
    switch (type) {
      case "Video":
        return { bg: "#fef3c7", text: "#92400e" };
      case "Article":
        return { bg: "#dbeafe", text: "#1e40af" };
      case "Template":
        return { bg: "#d1fae5", text: "#065f46" };
      case "Guide":
        return { bg: "#fce7f3", text: "#9f1239" };
      case "Glossary":
        return { bg: "#e0e7ff", text: "#3730a3" };
      default:
        return { bg: "#e0e7ff", text: "#3730a3" };
    }
  };

  return (
    <>
      <Navigation />
      <Box sx={{ bgcolor: "#f8fafc", minHeight: "100vh", py: 8 }}>
        <Container maxWidth="lg">
          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            align="center"
            sx={{ color: "#1e40af", fontWeight: 700, mb: 2 }}
          >
            Knowledge Center
          </Typography>
          <Typography
            variant="body1"
            align="center"
            sx={{ color: "#64748b", mb: 6, maxWidth: 700, mx: "auto" }}
          >
            Empower yourself with our curated collection of articles, videos,
            and tools to make informed insurance decisions.
          </Typography>

          <Grid container spacing={4}>
            {resources.map((resource, index) => {
              const chipColors = getChipColors(resource.type);
              return (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card
                    sx={{
                      height: "100%",
                      display: "flex",
                      flexDirection: "column",
                      transition: "all 0.3s ease",
                      borderRadius: "16px",
                      border: "1px solid #e5e7eb",
                      position: "relative",
                      overflow: "visible",
                      "&:hover": {
                        transform: "translateY(-8px)",
                        boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
                        borderColor: "#c7d2fe",
                      },
                    }}
                  >
                    {resource.disabled && (
                      <Chip
                        label="Coming Soon"
                        size="small"
                        sx={{
                          position: "absolute",
                          top: -10,
                          right: 16,
                          bgcolor: "#f59e0b",
                          color: "#ffffff",
                          fontWeight: 700,
                          fontSize: "0.65rem",
                          height: 24,
                          boxShadow: "0 2px 8px rgba(245, 158, 11, 0.4)",
                          zIndex: 1,
                        }}
                      />
                    )}
                    <CardContent
                      sx={{
                        flexGrow: 1,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        textAlign: "center",
                        p: 3,
                      }}
                    >
                      <Paper
                        elevation={0}
                        sx={{
                          background: getGradientForType(resource.type),
                          borderRadius: "50%",
                          width: 80,
                          height: 80,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          mb: 2,
                          boxShadow: "0 4px 15px rgba(0,0,0,0.15)",
                        }}
                      >
                        {resource.icon}
                      </Paper>

                      <Typography
                        variant="h6"
                        component="h3"
                        gutterBottom
                        sx={{ fontWeight: 600, color: "#1e293b" }}
                      >
                        {resource.title}
                      </Typography>

                      <Chip
                        label={resource.type}
                        size="small"
                        sx={{
                          mb: 2,
                          bgcolor: chipColors.bg,
                          color: chipColors.text,
                          fontWeight: 600,
                          fontSize: "0.7rem",
                        }}
                      />

                      <Typography
                        variant="body2"
                        sx={{
                          color: "#475569",
                          mb: 3,
                          flexGrow: 1,
                          lineHeight: 1.6,
                        }}
                      >
                        {resource.description}
                      </Typography>

                      <Button
                        variant="contained"
                        fullWidth
                        disabled={resource.disabled}
                        onClick={() => resource.path && navigate(resource.path)}
                        endIcon={<ArrowForward />}
                        sx={{
                          mt: "auto",
                          py: 1.2,
                          background: resource.disabled
                            ? "#e5e7eb"
                            : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                          color: "#ffffff",
                          fontWeight: 600,
                          fontSize: "0.9rem",
                          textTransform: "none",
                          borderRadius: "12px",
                          boxShadow: resource.disabled
                            ? "none"
                            : "0 4px 15px rgba(102, 126, 234, 0.4)",
                          transition: "all 0.3s ease",
                          "&:hover": {
                            background: resource.disabled
                              ? "#e5e7eb"
                              : "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
                            transform: resource.disabled
                              ? "none"
                              : "translateY(-2px)",
                            boxShadow: resource.disabled
                              ? "none"
                              : "0 6px 20px rgba(102, 126, 234, 0.5)",
                          },
                          "&.Mui-disabled": {
                            background: "#f3f4f6",
                            color: "#9ca3af",
                          },
                        }}
                      >
                        {resource.buttonText}
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>

          <Box sx={{ mt: 8, textAlign: "center" }}>
            <Typography variant="body2" sx={{ color: "#64748b", mb: 2 }}>
              More resources coming soon! Stay tuned for updates.
            </Typography>
          </Box>
        </Container>
      </Box>
    </>
  );
};

export default ResourcesPage;
