from request import Request
from database_connection import DatabaseConnection

# Simulating a function to get the logged-in user's sid (in a real application, this comes from session or authentication logic)
def get_logged_in_user_sid():
    return 140001  # Example logged-in user's SID

# Simulating a function to get the WFH request type from a submitted form
def get_request_type_from_form():
    return "All-day"  # Example form input, replace with actual form handling

# Simulating a function to get the user's decision from the UI (approve or reject)
def get_user_decision_from_ui():
    return "approve"  # This can be either 'approve' or 'reject'

def main():
    # Step 1: Initialize Database Connection
    db = DatabaseConnection()
    connection = db.connect()

    if connection:
        print("Connected to the database successfully!")

        # Step 2: Create a Request instance with the established connection
        request_handler = Request(connection)

        # Simulating a condition: request is only added if it's submitted through a form
        form_submission = True  # This would be True only if a form is submitted via the UI
        if form_submission:
            # Step 3: Retrieve the logged-in user's SID
            sid = get_logged_in_user_sid()  # Fetching the SID of the current logged-in user
            print(f"Logged-in user's SID: {sid}")

            # Step 4: Retrieve the WFH request type from the form submission
            request_type = get_request_type_from_form()  # Fetching the request type from form data
            print(f"Request type selected by the user: {request_type}")

            # Step 5: Add a new WFH request for the logged-in user
            new_request_id = request_handler.add_wfh_request(sid, request_type)
            print(f"New WFH request added with rid: {new_request_id}")
        else:
            print("No form submission detected, skipping request addition.")

        # Step 6: Retrieve the pending WFH request to approve/reject
        # In a real-world scenario, the pending request would be fetched from the database, e.g., via a request ID
        rid = 1  # Placeholder for request ID, this would come from the UI (e.g., via request selection)
        wfh_request = request_handler.get_request(rid)
        print(f"Retrieved WFH request: {wfh_request}")

        if wfh_request and wfh_request['status'] == "Pending":  # Check if the request is pending
            # Step 7: Get the user's decision (approve or reject) from the UI
            user_decision = get_user_decision_from_ui()  # This comes from the UI (which button the user clicked)
            print(f"User's decision: {user_decision}")

            # Step 8: Approve or Reject based on the user's decision
            if user_decision == "approve":
                # Call the approve method
                approve_status = request_handler.approve_wfh_request(rid)
                if approve_status:
                    print(f"Request {rid} approved successfully!")
                else:
                    print(f"Failed to approve request {rid}")
            elif user_decision == "reject":
                # Call the reject method
                reject_status = request_handler.reject_wfh_request(rid)
                if reject_status:
                    print(f"Request {rid} rejected successfully!")
                else:
                    print(f"Failed to reject request {rid}")
            else:
                print(f"Invalid user decision: {user_decision}")
        else:
            print("No pending WFH request found or request is not in 'Pending' status.")

        # Step 9: Close the database connection
        db.disconnect()
    else:
        print("Failed to connect to the database.")

if __name__ == "__main__":
    main()


