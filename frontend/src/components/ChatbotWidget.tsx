import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  CircularProgress,
  Fab,
  Chip,
  Tooltip,
  Rating,
  Fade,
  Divider,
} from "@mui/material";
import ChatIcon from "@mui/icons-material/Chat";
import SendIcon from "@mui/icons-material/Send";
import CloseIcon from "@mui/icons-material/Close";
import ThumbUpIcon from "@mui/icons-material/ThumbUp";
import ThumbDownIcon from "@mui/icons-material/ThumbDown";
import BotIcon from "@mui/icons-material/SmartToy";
import axios from "axios";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Array<{ id: string; url: string; score: number }>;
  timestamp: Date;
}

interface ChatbotWidgetProps {
  pageContext?: string;
  userProfile?: any;
}

const QUICK_QUESTIONS = [
  "What are pre-existing conditions?",
  "How do I file a health insurance claim?",
  "What is covered by health insurance?",
  "Explain co-payment",
];

const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({
  pageContext,
  userProfile,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! 👋 I'm your HealthNexus AI assistant. I can help you with health insurance questions. What would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text?: string) => {
    const messageText = text || inputText.trim();
    if (!messageText) return;

    // Add user message
    const userMessage: Message = {
      role: "user",
      content: messageText,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);

    try {
      // Call chatbot API
      const response = await axios.post(
        "http://localhost:5001/api/chat/query",
        {
          query: messageText,
          page_context: pageContext,
          top_k: 5,
          conversation_history: messages.slice(-6).map((m) => ({
            role: m.role,
            content: m.content,
          })),
          user_profile: userProfile,
        },
      );

      // Add assistant message
      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.answer,
        sources: response.data.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content:
          "I'm sorry, I'm having trouble responding right now. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    handleSendMessage(question);
  };

  const handleFeedback = async (messageIndex: number, rating: number) => {
    const message = messages[messageIndex];
    if (message.role !== "assistant") return;

    try {
      await axios.post("http://localhost:5001/api/chat/feedback", {
        query: messages[messageIndex - 1]?.content || "",
        answer: message.content,
        rating: rating,
      });
      setShowFeedback(messageIndex);
      setTimeout(() => setShowFeedback(null), 2000);
    } catch (error) {
      console.error("Feedback error:", error);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <Fab
          color="primary"
          sx={{
            position: "fixed",
            bottom: 24,
            right: 24,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "&:hover": {
              background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
            },
          }}
          onClick={() => setIsOpen(true)}
        >
          <ChatIcon />
        </Fab>
      )}

      {/* Chat Window */}
      <Fade in={isOpen}>
        <Paper
          elevation={8}
          sx={{
            position: "fixed",
            bottom: 24,
            right: 24,
            width: 380,
            maxWidth: "90vw",
            height: 600,
            maxHeight: "80vh",
            display: isOpen ? "flex" : "none",
            flexDirection: "column",
            borderRadius: 3,
            overflow: "hidden",
            zIndex: 1300,
          }}
        >
          {/* Header */}
          <Box
            sx={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
              p: 2,
              display: "flex",
              alignItems: "center",
              gap: 1,
            }}
          >
            <Avatar sx={{ bgcolor: "rgba(255,255,255,0.2)" }}>
              <BotIcon />
            </Avatar>
            <Box flexGrow={1}>
              <Typography variant="h6" fontWeight="bold">
                HealthNexus AI
              </Typography>
              <Typography variant="caption">Insurance Assistant</Typography>
            </Box>
            <IconButton
              size="small"
              sx={{ color: "white" }}
              onClick={() => setIsOpen(false)}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          {/* Messages */}
          <Box
            sx={{
              flexGrow: 1,
              overflowY: "auto",
              p: 2,
              bgcolor: "#f5f5f5",
            }}
          >
            {messages.map((message, index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent:
                      message.role === "user" ? "flex-end" : "flex-start",
                    mb: 0.5,
                  }}
                >
                  <Paper
                    elevation={1}
                    sx={{
                      p: 1.5,
                      maxWidth: "80%",
                      bgcolor: message.role === "user" ? "#667eea" : "white",
                      color: message.role === "user" ? "white" : "text.primary",
                      borderRadius: 2,
                    }}
                  >
                    <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                      {message.content}
                    </Typography>

                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <Box sx={{ mt: 1, pt: 1, borderTop: "1px solid #eee" }}>
                        <Typography variant="caption" color="text.secondary">
                          Sources:
                        </Typography>
                        {message.sources.map((source, idx) => (
                          <Chip
                            key={idx}
                            label={source.id}
                            size="small"
                            sx={{ ml: 0.5, mt: 0.5 }}
                          />
                        ))}
                      </Box>
                    )}
                  </Paper>
                </Box>

                {/* Feedback buttons for assistant messages */}
                {message.role === "assistant" && index > 0 && (
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "flex-start",
                      gap: 0.5,
                      ml: 1,
                    }}
                  >
                    {showFeedback === index ? (
                      <Typography variant="caption" color="success.main">
                        ✓ Feedback received
                      </Typography>
                    ) : (
                      <>
                        <Tooltip title="Helpful">
                          <IconButton
                            size="small"
                            onClick={() => handleFeedback(index, 1)}
                          >
                            <ThumbUpIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Not helpful">
                          <IconButton
                            size="small"
                            onClick={() => handleFeedback(index, -1)}
                          >
                            <ThumbDownIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </>
                    )}
                  </Box>
                )}
              </Box>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <Box
                sx={{ display: "flex", justifyContent: "flex-start", mb: 2 }}
              >
                <Paper elevation={1} sx={{ p: 1.5, borderRadius: 2 }}>
                  <CircularProgress size={20} />
                </Paper>
              </Box>
            )}

            <div ref={messagesEndRef} />
          </Box>

          {/* Quick Questions */}
          {messages.length === 1 && (
            <Box sx={{ p: 2, bgcolor: "white", borderTop: "1px solid #eee" }}>
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                mb={1}
              >
                Quick questions:
              </Typography>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                {QUICK_QUESTIONS.map((question, index) => (
                  <Chip
                    key={index}
                    label={question}
                    size="small"
                    onClick={() => handleQuickQuestion(question)}
                    clickable
                  />
                ))}
              </Box>
            </Box>
          )}

          {/* Input */}
          <Box sx={{ p: 2, bgcolor: "white", borderTop: "1px solid #eee" }}>
            <Box sx={{ display: "flex", gap: 1 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Ask a question..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                disabled={isLoading}
              />
              <IconButton
                color="primary"
                onClick={() => handleSendMessage()}
                disabled={!inputText.trim() || isLoading}
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>
      </Fade>
    </>
  );
};

export default ChatbotWidget;
