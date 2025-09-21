# Adding ESC Guidelines PDFs to Activate Full MedGraphRAG

This guide explains how to add ESC Guidelines PDFs to your deployed system to activate the full MedGraphRAG functionality.

## 🎯 Overview

Currently, your system is running in "basic mode" because no PDF guidelines are present. Once you add ESC Guidelines PDFs, the system will automatically:

- Process and chunk the PDFs using hierarchical chunking
- Generate semantic embeddings for hybrid search
- Enable full MedGraphRAG search with verification
- Activate safety validation features

## 📁 Where to Add PDFs

The system looks for PDF files in the `ESC_Guidelines/` directory. You have several options:

### Option 1: Direct GitHub Upload (Recommended for Testing)

1. **Navigate to your repository:**
   ```
   https://github.com/jdverbek/enhanced-esc-guidelines-search
   ```

2. **Go to the ESC_Guidelines folder:**
   - Click on the `ESC_Guidelines` folder in your repository
   - Click "Add file" → "Upload files"

3. **Upload PDF files:**
   - Drag and drop your ESC Guidelines PDF files
   - Commit the changes

4. **Render will automatically redeploy** with the new PDFs

### Option 2: Local Development Setup

If you're working locally:

```bash
# Clone the repository
git clone https://github.com/jdverbek/enhanced-esc-guidelines-search.git
cd enhanced-esc-guidelines-search

# Add your PDF files to the ESC_Guidelines directory
cp /path/to/your/esc-guidelines/*.pdf ESC_Guidelines/

# Commit and push
git add ESC_Guidelines/*.pdf
git commit -m "Add ESC Guidelines PDFs for MedGraphRAG processing"
git push origin main
```

### Option 3: Enable Full ML Dependencies First

For production use with large PDFs, you should first enable the full ML dependencies:

1. **Update requirements.txt:**
   ```bash
   # Edit requirements.txt to uncomment the ML libraries:
   PyMuPDF==1.23.8
   sentence-transformers==2.7.0
   pandas==2.1.4
   numpy==1.24.4
   torch==2.1.2
   transformers==4.36.2
   rank-bm25==0.2.2
   scikit-learn==1.3.2
   ```

2. **Update the main application:**
   - Replace `app.py` imports with `main_production.py` imports
   - This enables the full MedGraphRAG system

## 📋 Recommended ESC Guidelines

Here are the key ESC Guidelines you should add:

### Core Cardiovascular Guidelines:
- **ESC Guidelines for Heart Failure** (2021)
- **ESC Guidelines for Atrial Fibrillation** (2020)
- **ESC Guidelines for Acute Coronary Syndromes** (2020)
- **ESC Guidelines for Hypertension** (2018)
- **ESC Guidelines for Dyslipidaemias** (2019)
- **ESC Guidelines for Diabetes and CVD** (2019)

### File Naming Convention:
```
ESC_Guidelines/
├── esc-heart-failure-2021.pdf
├── esc-atrial-fibrillation-2020.pdf
├── esc-acute-coronary-syndromes-2020.pdf
├── esc-hypertension-2018.pdf
├── esc-dyslipidaemias-2019.pdf
└── esc-diabetes-cvd-2019.pdf
```

## 🔄 Automatic Processing

Once PDFs are added, the system will automatically:

1. **Detect new PDFs** on startup
2. **Process each PDF** using PyMuPDF
3. **Create hierarchical chunks** (parent + child relationships)
4. **Generate embeddings** using Sentence-BERT
5. **Build search indices** for hybrid retrieval
6. **Enable verification** and safety validation

## 📊 Monitoring Progress

You can monitor the processing progress:

### Check System Status:
```bash
curl https://esc-guidelines-search.onrender.com/system/status
```

### Check Guidelines List:
```bash
curl https://esc-guidelines-search.onrender.com/guidelines/list
```

### Check Logs:
- Go to your Render dashboard
- View the deployment logs to see processing progress

## ⚡ Quick Start for Testing

If you want to test immediately with a small PDF:

1. **Download a sample ESC guideline** (any recent ESC PDF)
2. **Upload to GitHub:**
   - Go to `ESC_Guidelines` folder in your repo
   - Upload the PDF file
   - Commit changes
3. **Wait for Render redeploy** (2-3 minutes)
4. **Test the enhanced search** on your live site

## 🚀 Expected Results

After adding PDFs, you should see:

- **System Status:** `"medgraph_rag": true`
- **Total Chunks:** > 0 (e.g., 1000+ chunks)
- **Enhanced Search:** Real medical content responses
- **Verification Scores:** Actual verification metrics
- **Safety Validation:** Working drug interaction checks

## 🔧 Troubleshooting

### If PDFs aren't processing:
1. **Check file size** - Keep PDFs under 50MB each
2. **Verify file format** - Must be valid PDF files
3. **Check logs** - Look for processing errors in Render logs
4. **Enable ML dependencies** - Uncomment libraries in requirements.txt

### If memory issues occur:
1. **Upgrade Render plan** - Free tier has memory limits
2. **Process fewer PDFs** - Start with 2-3 guidelines
3. **Optimize chunk sizes** - Reduce chunk size in configuration

## 📞 Support

If you encounter issues:
- Check the system logs in Render dashboard
- Test with a single small PDF first
- Verify the PDF files are valid and readable

---

**Ready to activate full MedGraphRAG? Start by uploading your first ESC Guidelines PDF!** 🎯
