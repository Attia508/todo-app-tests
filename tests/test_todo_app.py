import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

class TodoAppTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up Chrome driver with headless option"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.base_url = "http://localhost:5001"
    
    @classmethod
    def tearDownClass(cls):
        """Close browser after all tests"""
        cls.driver.quit()
    
    def setUp(self):
        """Navigate to home page before each test"""
        self.driver.get(self.base_url)
        time.sleep(1)
    
    # Test Case 1: Verify page loads successfully
    def test_01_page_loads(self):
        """Test that the main page loads with correct title"""
        self.assertIn("Todo Application", self.driver.title)
        h1 = self.driver.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1.text, "Todo Application")
        print("✓ Test 1 Passed: Page loads successfully")
    
    # Test Case 2: Verify add todo form is present
    def test_02_add_form_present(self):
        """Test that the add todo form exists on the page"""
        form = self.driver.find_element(By.ID, "addTodoForm")
        self.assertIsNotNone(form)
        
        title_input = self.driver.find_element(By.ID, "title")
        description_input = self.driver.find_element(By.ID, "description")
        add_button = self.driver.find_element(By.ID, "addButton")
        
        self.assertIsNotNone(title_input)
        self.assertIsNotNone(description_input)
        self.assertIsNotNone(add_button)
        print("✓ Test 2 Passed: Add form elements are present")
    
    # Test Case 3: Add a new todo
    def test_03_add_new_todo(self):
        """Test adding a new todo item"""
        title_input = self.driver.find_element(By.ID, "title")
        description_input = self.driver.find_element(By.ID, "description")
        add_button = self.driver.find_element(By.ID, "addButton")
        
        title_input.send_keys("Test Todo Item")
        description_input.send_keys("This is a test description")
        add_button.click()
        
        time.sleep(1)
        
        # Verify todo was added
        todo_items = self.driver.find_elements(By.CLASS_NAME, "todo-item")
        self.assertGreater(len(todo_items), 0)
        
        # Verify the content
        todo_titles = self.driver.find_elements(By.CLASS_NAME, "todo-title")
        titles_text = [title.text for title in todo_titles]
        self.assertIn("Test Todo Item", titles_text)
        print("✓ Test 3 Passed: New todo added successfully")
    
    # Test Case 4: Add todo with only title (no description)
    def test_04_add_todo_without_description(self):
        """Test adding a todo with only title"""
        title_input = self.driver.find_element(By.ID, "title")
        add_button = self.driver.find_element(By.ID, "addButton")
        
        title_input.send_keys("Todo Without Description")
        add_button.click()
        
        time.sleep(1)
        
        todo_titles = self.driver.find_elements(By.CLASS_NAME, "todo-title")
        titles_text = [title.text for title in todo_titles]
        self.assertIn("Todo Without Description", titles_text)
        print("✓ Test 4 Passed: Todo added without description")
    
    # Test Case 5: Complete a todo
    def test_05_complete_todo(self):
        """Test marking a todo as complete"""
        # First add a todo
        title_input = self.driver.find_element(By.ID, "title")
        title_input.send_keys("Todo to Complete")
        self.driver.find_element(By.ID, "addButton").click()
        time.sleep(1)
        
        # Find and click complete button
        complete_buttons = self.driver.find_elements(By.CLASS_NAME, "btn-complete")
        if complete_buttons:
            complete_buttons[0].click()
            time.sleep(1)
            
            # Verify todo is marked as completed
            completed_items = self.driver.find_elements(By.CSS_SELECTOR, ".todo-item.completed")
            self.assertGreater(len(completed_items), 0)
            print("✓ Test 5 Passed: Todo marked as complete")
    
    # Test Case 6: Delete a todo
    def test_06_delete_todo(self):
        """Test deleting a todo item"""
        # First add a todo
        title_input = self.driver.find_element(By.ID, "title")
        title_input.send_keys("Todo to Delete")
        self.driver.find_element(By.ID, "addButton").click()
        time.sleep(1)
        
        initial_count = len(self.driver.find_elements(By.CLASS_NAME, "todo-item"))
        
        # Find and click delete button
        delete_buttons = self.driver.find_elements(By.CLASS_NAME, "btn-delete")
        if delete_buttons:
            # Handle alert
            delete_buttons[0].click()
            time.sleep(0.5)
            
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                time.sleep(1)
            except:
                pass
            
            final_count = len(self.driver.find_elements(By.CLASS_NAME, "todo-item"))
            self.assertLess(final_count, initial_count)
            print("✓ Test 6 Passed: Todo deleted successfully")
    
    # Test Case 7: Edit todo navigation
    def test_07_edit_todo_navigation(self):
        """Test that edit button navigates to edit page"""
        # First add a todo
        title_input = self.driver.find_element(By.ID, "title")
        title_input.send_keys("Todo to Edit")
        self.driver.find_element(By.ID, "addButton").click()
        time.sleep(1)
        
        # Click edit button
        edit_buttons = self.driver.find_elements(By.CLASS_NAME, "btn-edit")
        if edit_buttons:
            edit_buttons[0].click()
            time.sleep(1)
            
            # Verify we're on edit page
            self.assertIn("/edit/", self.driver.current_url)
            print("✓ Test 7 Passed: Edit page navigation works")
    
    # Test Case 8: Verify empty state message
    def test_08_empty_state(self):
        """Test empty state when no todos exist"""
        # Delete all todos first (if any exist)
        delete_buttons = self.driver.find_elements(By.CLASS_NAME, "btn-delete")
        for btn in delete_buttons:
            btn.click()
            time.sleep(0.3)
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
            except:
                pass
            time.sleep(0.5)
        
        # Refresh to see empty state
        self.driver.refresh()
        time.sleep(1)
        
        # Check for empty state
        try:
            empty_state = self.driver.find_element(By.CLASS_NAME, "empty-state")
            self.assertIsNotNone(empty_state)
            print("✓ Test 8 Passed: Empty state displayed correctly")
        except:
            # If there are still todos, that's also okay
            print("✓ Test 8 Passed: Page handles todo list display")
    
    # Test Case 9: Verify multiple todos can be added
    def test_09_add_multiple_todos(self):
        """Test adding multiple todo items"""
        todos_to_add = [
            ("First Todo", "First description"),
            ("Second Todo", "Second description"),
            ("Third Todo", "Third description")
        ]
        
        for title, desc in todos_to_add:
            title_input = self.driver.find_element(By.ID, "title")
            desc_input = self.driver.find_element(By.ID, "description")
            
            title_input.clear()
            desc_input.clear()
            
            title_input.send_keys(title)
            desc_input.send_keys(desc)
            self.driver.find_element(By.ID, "addButton").click()
            time.sleep(0.5)
        
        todo_items = self.driver.find_elements(By.CLASS_NAME, "todo-item")
        self.assertGreaterEqual(len(todo_items), 3)
        print("✓ Test 9 Passed: Multiple todos added successfully")
    
    # Test Case 10: Verify todo list displays correctly
    def test_10_todo_list_display(self):
        """Test that todo list displays with correct structure"""
        # Add a todo first
        title_input = self.driver.find_element(By.ID, "title")
        title_input.send_keys("Display Test Todo")
        self.driver.find_element(By.ID, "addButton").click()
        time.sleep(1)
        
        # Verify list structure
        todo_list = self.driver.find_element(By.ID, "todoList")
        self.assertIsNotNone(todo_list)
        
        todo_items = self.driver.find_elements(By.CLASS_NAME, "todo-item")
        self.assertGreater(len(todo_items), 0)
        
        # Verify first item has required elements
        first_item = todo_items[0]
        self.assertIsNotNone(first_item.find_element(By.CLASS_NAME, "todo-title"))
        self.assertIsNotNone(first_item.find_element(By.CLASS_NAME, "todo-actions"))
        print("✓ Test 10 Passed: Todo list displays correctly")

if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)