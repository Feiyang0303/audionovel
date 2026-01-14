# MongoDB Setup Guide for AudioNovel

This guide will help you set up MongoDB for the AudioNovel application. MongoDB is used to store file uploads, processing results, and application data.

## Quick Start

1. **Run the setup script:**
   ```bash
   cd backend
   python setup_mongodb.py
   ```

2. **Follow the interactive prompts** to configure MongoDB

3. **Test the connection:**
   ```bash
   python test_mongodb.py
   ```

4. **Start the application:**
   ```bash
   python app.py
   ```

## MongoDB Options

### Option 1: MongoDB Atlas (Recommended - Cloud Database)

MongoDB Atlas provides a free cloud database that's perfect for development and small applications.

#### Setup Steps:

1. **Create MongoDB Atlas Account:**
   - Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Sign up for a free account
   - Create a new cluster (choose the free tier)

2. **Configure Database Access:**
   - Go to "Database Access" in the left sidebar
   - Click "Add New Database User"
   - Create a username and password
   - Select "Read and write to any database"
   - Click "Add User"

3. **Configure Network Access:**
   - Go to "Network Access" in the left sidebar
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (for development)
   - Click "Confirm"

4. **Get Connection String:**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database password
   - Replace `<dbname>` with `audionovel`

#### Example Connection String:
```
mongodb+srv://username:password@cluster.mongodb.net/audionovel?retryWrites=true&w=majority
```

### Option 2: Local MongoDB

If you prefer to run MongoDB locally on your machine.

#### macOS Setup:
```bash
# Install MongoDB using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community
```

#### Ubuntu/Debian Setup:
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Create list file for MongoDB
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package database
sudo apt-get update

# Install MongoDB
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### Windows Setup:
1. Download MongoDB Community Server from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Run the installer and follow the setup wizard
3. MongoDB will run as a Windows service automatically

#### Docker Setup (Alternative):
```bash
# Run MongoDB in Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# To stop and remove the container
docker stop mongodb
docker rm mongodb
```

#### Local Connection String:
```
mongodb://localhost:27017/audionovel
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/audionovel?retryWrites=true&w=majority

# Qwen API Key (for text processing)
QWEN_API_KEY=your_qwen_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### Database Collections

The application automatically creates the following collections:

#### `files` Collection
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
  "target_age_group": "8-12",
  "created_at": "2024-06-24T16:15:00Z",
  "updated_at": "2024-06-24T16:15:00Z"
}
```

#### `processing_results` Collection
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
  "status": "completed",
  "created_at": "2024-06-24T16:15:00Z",
  "updated_at": "2024-06-24T16:15:00Z"
}
```

## API Endpoints

The application provides the following MongoDB-related API endpoints:

### File Management
- `GET /files` - List all uploaded files
- `GET /files/<file_id>` - Get detailed file information
- `DELETE /files/<file_id>` - Delete a file and its processing result
- `GET /files/status/<status>` - Get files by status
- `GET /files/type/<file_type>` - Get files by file type

### Processing Results
- `GET /status/<filename>` - Get processing status for a file
- `GET /files/<file_id>` - Get file details with processing results

### Statistics
- `GET /stats` - Get database statistics

## Testing

### Test MongoDB Connection
```bash
python test_mongodb.py
```

### Test File Upload and Processing
```bash
python test_upload.py
```

## Troubleshooting

### Common Issues

1. **Connection Failed:**
   - Check if MongoDB is running
   - Verify connection string format
   - Ensure network access is configured (for Atlas)
   - Check firewall settings

2. **Authentication Failed:**
   - Verify username and password
   - Check database user permissions
   - Ensure database name is correct

3. **Index Creation Failed:**
   - This is normal for the first run
   - Indexes will be created automatically

### MongoDB Compass

MongoDB Compass is a GUI for MongoDB. You can use it to:
- View your collections
- Browse documents
- Run queries
- Monitor database performance

Download from: https://www.mongodb.com/try/download/compass

### Logs

Check the application logs for MongoDB-related errors:
```bash
python app.py
```

## Performance Optimization

The application includes several performance optimizations:

1. **Database Indexes:** Automatically created for common queries
2. **Connection Pooling:** Efficient connection management
3. **Batch Operations:** Optimized for bulk operations
4. **Caching:** Results are cached to reduce database load

## Security Considerations

1. **Environment Variables:** Never commit `.env` files to version control
2. **Network Access:** Restrict network access in production
3. **User Permissions:** Use least privilege principle for database users
4. **Connection String:** Keep connection strings secure

## Backup and Recovery

### MongoDB Atlas
- Automatic backups are included with Atlas
- Manual backups can be created from the Atlas dashboard

### Local MongoDB
```bash
# Create backup
mongodump --db audionovel --out /backup/path

# Restore backup
mongorestore --db audionovel /backup/path/audionovel
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review MongoDB logs
3. Test with the provided test scripts
4. Check the MongoDB documentation: https://docs.mongodb.com/ 