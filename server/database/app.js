import express, { raw } from "express";
import { connect } from "mongoose";
import { readFileSync } from "fs";
import bodyParser from "body-parser";
import cors from "cors";
const app = express();
const port = 3030;

app.use(cors());
app.use(bodyParser.urlencoded({ extended: false }));

const reviews_data = JSON.parse(readFileSync("reviews.json", "utf8"));
const dealerships_data = JSON.parse(readFileSync("dealerships.json", "utf8"));

connect("mongodb://mongo_db:27017/", { dbName: "dealershipsDB" });

import Reviews from "./review.js";
import Dealerships from "./dealership.js";

const deleteReviews = () => Reviews.deleteMany();
const addReviews = (data) => Reviews.insertMany(data);
const findReviews = (query) => Reviews.find(query);

const deleteDealerships = () => Dealerships.deleteMany();
const addDealerships = (data) => Dealerships.insertMany(data);
const findDealerships = (query) => Dealerships.find(query);

try {
  deleteReviews({}).then(() => {
    addReviews(reviews_data["reviews"]);
  });
  deleteDealerships({}).then(() => {
    addDealerships(dealerships_data["dealerships"]);
  });
} catch (error) {
  console.error("Error loading DB on application start:", error);
}

// Express route to home
app.get("/", async (_req, res) => {
  res.send("Welcome to the Mongoose API");
});

// Express route to fetch all reviews
app.get("/fetchReviews", async (_req, res) => {
  try {
    const documents = await findReviews();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: "Error fetching documents" });
  }
});

// Express route to fetch reviews by a particular dealer
app.get("/fetchReviews/dealer/:id", async (req, res) => {
  try {
    const documents = await findReviews({ dealership: req.params.id });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: "Error fetching documents" });
  }
});

// Express route to fetch all dealerships
app.get("/fetchDealers", async (req, res) => {
  try {
    const allDealerships = await findDealerships();
    res.json(allDealerships);
  } catch (error) {
    res.status(500).json({ error: "Error fetching dealerships" });
  }
});

// Express route to fetch Dealers by a particular state
app.get("/fetchDealers/:state", async (req, res) => {
  try {
    const stateDealerships = await findDealerships({
      state: req.params.state,
    });
    res.json(stateDealerships);
  } catch (error) {
    res.status(500).json({ error: "Error fetching dealerships by state" });
  }
});

// Express route to fetch dealer by a particular id
app.get("/fetchDealer/:id", async (req, res) => {
  try {
    const dealserhip = await findDealerships({
      id: req.params.id,
    });
    res.json(dealserhip);
  } catch (error) {
    res.status(500).json({ error: `Error finding dealership with ID: ${id}` });
  }
});

//Express route to insert review
app.post("/insert_review", raw({ type: "*/*" }), async (req, res) => {
  data = JSON.parse(req.body);
  const documents = await findReviews().sort({ id: -1 });
  let new_id = documents[0]["id"] + 1;

  const review = new Reviews({
    id: new_id,
    name: data["name"],
    dealership: data["dealership"],
    review: data["review"],
    purchase: data["purchase"],
    purchase_date: data["purchase_date"],
    car_make: data["car_make"],
    car_model: data["car_model"],
    car_year: data["car_year"],
  });

  try {
    const savedReview = await review.save();
    res.json(savedReview);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: "Error inserting review" });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
