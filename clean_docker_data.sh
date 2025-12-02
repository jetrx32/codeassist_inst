docker stop codeassist-zero-style-ui codeassist-solution-tester codeassist-state-service codeassist-web-ui codeassist-policy-model codeassist-ollama
docker rm codeassist-zero-style-ui codeassist-solution-tester codeassist-state-service codeassist-web-ui codeassist-policy-model codeassist-ollama
docker network rm codeassist_network
docker system prune -a -f
