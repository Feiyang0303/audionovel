# MongoDB Setup Guide

## Option 1: MongoDB Atlas (Recommended - Cloud Database)

### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Sign up for a free account
3. Create a new cluster (choose the free tier)

### Step 2: Get Connection String
1. In your cluster, click "Connect"
2. Choose "Connect your application"
3. Copy the connection string
4. Replace `<password>` with your database password
5. Replace `<dbname>` with `audionovel`

### Step 3: Set Environment Variable
Create a `.env` file in the backend directory:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/audionovel?retryWrites=true&w=majority
QWEN_API_KEY=your_qwen_api_key
```

## Option 2: Local MongoDB (Alternative)

If you prefer to run MongoDB locally:

### Install MongoDB Community Edition
```bash
# Download from MongoDB website
# https://www.mongodb.com/try/download/community

# Or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Connection String for Local
```
MONGODB_URI=mongodb://localhost:27017/audionovel
```

## Testing the Connection

Once MongoDB is set up, you can test it by running:
```bash
cd backend
python app.py
```

The application will automatically:
1. Connect to MongoDB
2. Create the necessary collections
3. Start the Flask server

## Database Collections

The application creates two main collections:

### `files` Collection
Stores information about uploaded files:
```json
{
  "_id": "ObjectId",
  "filename": "test.txt",
  "original_filename": "test.txt",
  "file_path": "/path/to/file",
  "file_size": 1234,
  "file_type": "txt",
  "upload_date": "2024-06-24T16:15:00Z",
  "status": "completed",
  "target_age_group": "8-12"
}
```

### `processing_results` Collection
Stores processing results and analysis:
```json
{
  "_id": "ObjectId",
  "file_id": "file_object_id",
  "simplified_text": "NARRATOR: This is a story...",
  "characters": [
    {"name": "Narrator", "dialogue_count": 5}
  ],
  "expert_analyses": {
    "subject_researcher": "Analysis text...",
    "case_analyst": "More analysis..."
  },
  "processing_steps": [
    {"role": "Subject Researcher", "status": "completed"}
  ],
  "processing_date": "2024-06-24T16:15:00Z",
  "processing_duration": 268.5,
  "status": "completed"
}
```

## Using MongoDB Compass

MongoDB Compass is a GUI for MongoDB. You can use it to:
1. View your collections
2. Browse documents
3. Run queries
4. Monitor database performance

Open MongoDB Compass and connect using your connection string to explore your data. 