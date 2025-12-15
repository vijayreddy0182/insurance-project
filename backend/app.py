# backend/app.py
from flask import Flask, request, jsonify, send_from_directory
from db import get_connection
import re

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path="/"
)

# Serve frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# API to list all policies
@app.route("/api/policies")
def list_policies():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT PolicyID, PolicyCode, PolicyName, Premium FROM dbo.Policies")
        rows = cur.fetchall()

        policies = [
            {
                "PolicyID": r.PolicyID,
                "PolicyCode": r.PolicyCode,
                "PolicyName": r.PolicyName,
                "Premium": float(r.Premium),
            }
            for r in rows
        ]

        cur.close()
        conn.close()
        return jsonify(policies)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# API to submit insurance application
@app.route("/api/submit", methods=["POST"])
def submit_application():
    data = request.json

    # Validate phone number (exactly 10 digits)
    phone = data.get("phone", "")
    if not re.fullmatch(r"\d{10}", phone):
        return jsonify({"success": False, "error": "Phone number must be exactly 10 digits"}), 400

    # Validate full name
    full_name = data.get("fullName", "").strip()
    if not full_name:
        return jsonify({"success": False, "error": "Full name is required"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Convert numeric fields
        coverage = data.get("coverage")
        if coverage:
            coverage = float(coverage)

        policy_id = data.get("policyId")
        if policy_id in ("", None):
            policy_id = None
        else:
            policy_id = int(policy_id)

        # Use transaction to ensure both inserts succeed or rollback
        conn.autocommit = False
        try:
            # Insert customer and get ID
            cur.execute(
                """
                INSERT INTO dbo.Customers (FullName, Email, Phone, DateOfBirth, Address)
                OUTPUT INSERTED.CustomerID
                VALUES (?, ?, ?, ?, ?)
                """,
                full_name,
                data.get("email"),
                phone,
                data.get("dob"),
                data.get("address"),
            )

            row = cur.fetchone()
            if row and row[0] is not None:
                customer_id = row[0]
            else:
                conn.rollback()
                return jsonify({"success": False, "error": "Failed to get CustomerID"}), 500

            # Insert application
            cur.execute(
                """
                INSERT INTO dbo.Applications (CustomerID, PolicyID, CoverageAmount, StartDate, Notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                customer_id,
                policy_id,
                coverage,
                data.get("startDate"),
                data.get("notes"),
            )

            conn.commit()
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "error": f"Transaction failed: {str(e)}"}), 500
        finally:
            cur.close()
            conn.close()

        return jsonify({"success": True, "customerId": customer_id}), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
