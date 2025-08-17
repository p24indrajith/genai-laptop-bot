FROM flowiseai/flowise:latest

# Expose Flowise default port
EXPOSE 3000

# Run Flowise
CMD ["npm", "run", "start"]
