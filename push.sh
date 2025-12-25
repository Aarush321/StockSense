#!/bin/bash
# Push script for StockSense
# Make sure you have a GitHub Personal Access Token ready

echo "🚀 Pushing StockSense to GitHub..."
echo ""
echo "Repository: https://github.com/Aarush321/StockSense"
echo ""
echo "If prompted for credentials:"
echo "  Username: Aarush321"
echo "  Password: [Your Personal Access Token - NOT your GitHub password]"
echo ""
echo "Get a token at: https://github.com/settings/tokens/new"
echo ""

cd /Users/aarushravichandran/Desktop/Code/StockAnalysisTool
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "📦 Repository: https://github.com/Aarush321/StockSense"
    echo ""
    echo "Next steps:"
    echo "1. Deploy backend to Render (see DEPLOYMENT.md)"
    echo "2. Deploy frontend to Netlify (see DEPLOYMENT.md)"
else
    echo ""
    echo "❌ Push failed. Make sure you:"
    echo "1. Have a Personal Access Token (https://github.com/settings/tokens/new)"
    echo "2. Use the token as your password (not your GitHub password)"
    echo "3. Username should be: Aarush321"
fi

