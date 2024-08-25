Here is the updated API documentation in Markdown format, including the new endpoints:

---

# Chat Group API Documentation

## Endpoints

### 1. **Create a New Chat Group**
   - **URL:** `/chatrooms/<user_id>/create/`
   - **Method:** `POST`
   - **Description:** Creates a new chat group with the specified members. The user creating the group becomes the owner and admin by default.
   - **Request Body:** 
     ```json
     {
       "group_name": "string",
       "group_description": "string",
       "organization": "int",
       "members": ["int", "int"]
     }
     ```
   - **Response:**
     - **201 Created:** Returns the details of the created chat group.
     - **404 Not Found:** If the user or organization does not exist.

### 2. **Edit Chat Group**
   - **URL:** `/chatrooms/<chatroom_id>/<user_id>/edit/`
   - **Method:** `PUT`
   - **Description:** Edit the name and description of a chat group. Only admins can edit.
   - **Request Body:** 
     ```json
     {
       "group_name": "string",
       "group_description": "string"
     }
     ```
   - **Response:**
     - **200 OK:** Returns the updated chat group details.
     - **404 Not Found:** If the chat group or admin is not found.

### 3. **Delete Chat Group**
   - **URL:** `/chatrooms/<chatroom_id>/<user_id>/delete/`
   - **Method:** `DELETE`
   - **Description:** Delete a chat group. Only the owner can delete the group.
   - **Response:**
     - **204 No Content:** If deletion is successful.
     - **404 Not Found:** If the chat group or owner is not found.

### 4. **Add Users to Chat Group**
   - **URL:** `/chatrooms/<chatroom_id>/<admin_id>/add-users/`
   - **Method:** `POST`
   - **Description:** Add multiple users to a chat group. Only admins can add users.
   - **Request Body:** 
     ```json
     {
       "users": ["int", "int"]
     }
     ```
   - **Response:**
     - **200 OK:** If users are added successfully.
     - **404 Not Found:** If the chat group or admin is not found.

### 5. **Add User to Chat Group**
   - **URL:** `/chatrooms/<chatroom_id>/<admin_id>/add-user/`
   - **Method:** `POST`
   - **Description:** Add a single user to a chat group. Only admins can add users.
   - **Request Body:** 
     ```json
     {
       "user_id": "int"
     }
     ```
   - **Response:**
     - **200 OK:** If the user is added successfully.
     - **404 Not Found:** If the chat group or admin is not found.

### 6. **Remove Multiple Members from Chat Group**
   - **URL:** `/chatrooms/<chatroom_id>/<admin_id>/remove-members/`
   - **Method:** `DELETE`
   - **Description:** Remove multiple members from a chat group. Also removes them from the admin list if they are admins.
   - **Request Body:** 
     ```json
     {
       "users": ["int", "int"]
     }
     ```
   - **Response:**
     - **200 OK:** If the users are removed successfully.
     - **404 Not Found:** If the chat group or admin is not found.

### 7. **Remove Member from Chat Group**
   - **URL:** `/chatrooms/<chatroom_id>/<admin_id>/remove-member/`
   - **Method:** `DELETE`
   - **Description:** Remove a single member from a chat group. Also removes them from the admin list if they are an admin.
   - **Request Body:** 
     ```json
     {
       "user_id": "int"
     }
     ```
   - **Response:**
     - **200 OK:** If the user is removed successfully.
     - **404 Not Found:** If the chat group or admin is not found.

### 8. **Add Admins to Chat Group**
   - **URL:** `/chatrooms/<chatroom_id>/<owner_id>/add-admins/`
   - **Method:** `POST`
   - **Description:** Add multiple users as admins to a chat group. Only the owner can add admins.
   - **Request Body:** 
     ```json
     {
       "users": ["int", "int"]
     }
     ```
   - **Response:**
     - **200 OK:** If the admins are added successfully.
     - **404 Not Found:** If the chat group or owner is not found.

### 9. **Add Admin to Chat Group**
   - **URL:** `/chatrooms/<chatroom_id>/<owner_id>/add-admin/`
   - **Method:** `POST`
   - **Description:** Add a single user as an admin to a chat group. Only the owner can add admins.
   - **Request Body:** 
     ```json
     {
       "user_id": "int"
     }
     ```
   - **Response:**
     - **200 OK:** If the admin is added successfully.
     - **404 Not Found:** If the chat group or owner is not found.

### 10. **Remove Admins from Chat Group**
   - **URL:** `/chatrooms/<chatroom_id>/<owner_id>/remove-admins/`
   - **Method:** `DELETE`
   - **Description:** Remove multiple admins from a chat group. Only the owner can remove admins.
   - **Request Body:** 
     ```json
     {
       "users": ["int", "int"]
     }
     ```
   - **Response:**
     - **200 OK:** If the admins are removed successfully.
     - **404 Not Found:** If the chat group or owner is not found.

### 11. **Remove Admin from Chat Group**
   - **URL:** `/chatrooms/<chatroom_id>/<owner_id>/remove-admin/`
   - **Method:** `DELETE`
   - **Description:** Remove a single admin from a chat group. Only the owner can remove admins.
   - **Request Body:** 
     ```json
     {
       "user_id": "int"
     }
     ```
   - **Response:**
     - **200 OK:** If the admin is removed successfully.
     - **404 Not Found:** If the chat group or owner is not found.

### 12. **Get All Chat Groups in an Organization**
   - **URL:** `/chatrooms/<organization_id>/list/`
   - **Method:** `GET`
   - **Description:** Retrieve all chat groups that belong to a specific organization.
   - **Response:**
     - **200 OK:** Returns a list of all chat groups in the organization.
     - **404 Not Found:** If no chat groups are found for the organization.

### 13. **Get All Chat Groups a User is a Member Of**
   - **URL:** `/chatrooms/<organization_id>/<user_id>/list/`
   - **Method:** `GET`
   - **Description:** Retrieve all chat groups that a specific user is a member of within an organization.
   - **Response:**
     - **200 OK:** Returns a list of all chat groups the user is a member of within the organization.
     - **404 Not Found:** If no chat groups are found for the user in the organization.

### 14. **Get a Specific Chat Group by ID**
   - **URL:** `/chatrooms/<chatroom_id>/<user_id>/view/`
   - **Method:** `GET`
   - **Description:** Retrieve details of a specific chat group by its ID. The user must be a member of the chat group.
   - **Response:**
     - **200 OK:** Returns the details of the specified chat group.
     - **404 Not Found:** If the chat group is not found or the user is not a member.

---

Save the above content in a file named `API_Documentation.md`.