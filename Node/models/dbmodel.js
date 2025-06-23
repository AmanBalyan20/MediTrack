const mongoose = require('mongoose');

const consumptionSchema = new mongoose.Schema({
    patient_id: {
        type: String,
        required: true,
    },
    consumption_date: {
        type: Date,
        default: Date.now,
    },
    dosage: {
        type: String,
        required: true,
    },
    consumption_frequency: {
        type: String,
        required: true,
    },
    pattern_details: {
        type: String,
        required: true,
    },
    prescription_image: {
        type: [String], 
        required: true,
    },
    medicines_purchase: {
        type: [String], 
        required: true,
    },
});



module.exports = mongoose.model('consumption', consumptionSchema)    

