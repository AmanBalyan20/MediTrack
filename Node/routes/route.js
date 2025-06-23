const express = require('express')
const router  = express.Router()
const validator  =require('../middlewares/validator')
const axios = require("axios");
const consumption = require('../models/dbmodel');
const multer = require('multer');
const AWS = require('aws-sdk');
require('dotenv').config();


// This is the signing api
router.post("/signin", async (req, res) => {
    const { email, password } = req.body;
 
    try {
        const response = await axios.post("http://localhost:3999/signin", {
            email,
            password,
        });
 
        if (response.status === 200) {
            const token = response.data.token; 
            return res.json({ message: "Sign-in successful", token });
        } else {
            return res.status(response.status).json({ error: response.data.error });
        }
    } catch (error) {
        const errorMessage = error.response?.data?.error || "Sign-in failed";
        return res.status(error.response?.status || 500).json({ error: errorMessage });
    }
});


// Validating the api whether the given token is valid or not 
router.get('/users' ,validator ,async (req, res) => {
    try {
        const regions = await consumption.find();
        res.status(200).json(regions); 
    } catch (err) {
        res.status(500).json({ error: `Failed to fetch regions: ${err.message}` });
    }
});


// gettihn the data form the database using patient id 
router.get('/prescription/:patient_id/data', validator, async (req, res) => {
    const { patient_id } = req.params;
    try {
        const prescriptions = await consumption.find({ patient_id });

        if (prescriptions.length === 0) {
            return res.status(404).json({ message: "No prescriptions found for the given patient ID" });
        }
        const response = prescriptions.map(prescription => ({
            patient_id: prescription.patient_id,
            prescription_url: prescription.prescription_image,
        }));

        res.status(200).json(response);
    } catch (error) {
        res.status(500).json({ message: `Failed to fetch prescriptions: ${error.message}` });
    }
});

// Posting the data to the database collection  
AWS.config.update({
    accessKeyId: process.env.ACCESS_KEY,
    secretAccessKey:process.env.SECRET_ACCESS_KEY ,
    region: process.env.REGION,
});
 
const s3 = new AWS.S3();
 
const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 5 * 1024 * 1024 }, 
});
 
// Define the upload endpoint
router.post("/record/create", validator,
    upload.fields([
        { name: "prescription_image", maxCount: 1 },
        { name: "medicines_purchase", maxCount: 1 },
    ]), async (req, res) => {
        try {
            const { patient_id, consumption_date, dosage, consumption_frequency, pattern_details, } = req.body;
            const files = req.files;
 
            if (!files.prescription_image || !files.medicines_purchase || !patient_id || !consumption_date || !dosage || !consumption_frequency || !pattern_details) {
                return res.status(400).json({ error: "All fields and files are required." });
            }
 
            const bucketName = process.env.BUCKET_NAME;
 
            // Helper function to upload a file to S3
            const uploadFileToS3 = async (file, folderName) => {
                const objectKey = `${folderName}/${Date.now()}_${file.originalname}`;
                const params = {
                    Bucket: bucketName,
                    Key: objectKey,
                    Body: file.buffer,
                    ContentType: file.mimetype,
                };
 
                await s3.upload(params).promise();
                return s3.getSignedUrl("getObject", {
                    Bucket: bucketName,
                    Key: objectKey,
                    Expires: 3600,
                });
            };
 
            // Upload files to S3
            const prescriptionImageUrl = await uploadFileToS3(
                files.prescription_image[0],
                "prescription_image"
            );
            const medicinesPurchaseUrl = await uploadFileToS3(
                files.medicines_purchase[0],
                "medicines_purchase"
            );
 
            // Construct record
            const record = { patient_id, consumption_date, dosage, consumption_frequency, pattern_details, prescription_image: prescriptionImageUrl, medicines_purchase: medicinesPurchaseUrl,
            };

            const data = await consumption.insertMany(record)
 
            // Respond with the record
            res.status(200).json({
                message: "Record created and files uploaded successfully.",
                data: record,
            });
        } catch (error) {
            console.error("Error uploading files and creating record:", error);
            res.status(500).json({ error: "Error uploading files or creating record." });
        }
    }
);
 
 


// Delete
router.delete('/prescription/:patient_id', validator , async (req, res) => {
    const { patient_id } = req.params;

    try {
        const deletedDocument = await consumption.findOneAndDelete({ patient_id });

        if (!deletedDocument) {
            return res.status(404).json({ message: "No document found with the given patient ID" });
        }

        res.status(200).json({ message: "Document deleted successfully", deletedDocument });
    } catch (error) {
        res.status(500).json({ message: `Failed to delete document: ${error.message}` });
    }
});



module.exports = router;