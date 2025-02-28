package main

import (
	"fmt"
	"time"
)

// UserService manages user-related operations
type UserService struct {
	repository *UserRepository
	logger     *Logger
}

// NewUserService creates a new UserService
func NewUserService(repo *UserRepository, logger *Logger) *UserService {
	return &UserService{
		repository: repo,
		logger:     logger,
	}
}

// GetUser retrieves a user by ID
func (s *UserService) GetUser(id string) (*User, error) {
	s.logger.Info(fmt.Sprintf("Fetching user with ID: %s", id))
	user, err := s.repository.FindByID(id)
	if err != nil {
		s.logger.Error(fmt.Sprintf("Error fetching user: %v", err))
		return nil, err
	}
	return user, nil
}

// CreateUser creates a new user
func (s *UserService) CreateUser(name, email string) (*User, error) {
	user := s.buildUser(name, email)
	err := s.repository.Save(user)
	if err != nil {
		return nil, err
	}
	s.sendWelcomeEmail(user)
	return user, nil
}

// UpdateUser updates an existing user
func (s *UserService) UpdateUser(id, name, email string) (*User, error) {
	user, err := s.repository.FindByID(id)
	if err != nil {
		return nil, err
	}
	
	user.Name = name
	user.Email = email
	user.UpdatedAt = time.Now()
	
	err = s.repository.Save(user)
	if err != nil {
		return nil, err
	}
	
	return user, nil
}

// buildUser creates a new User instance
func (s *UserService) buildUser(name, email string) *User {
	return &User{
		ID:        generateID(),
		Name:      name,
		Email:     email,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
}

// sendWelcomeEmail sends a welcome email to new users
func (s *UserService) sendWelcomeEmail(user *User) {
	s.logger.Info(fmt.Sprintf("Sending welcome email to %s", user.Email))
	// Email sending logic would go here
}

// generateID generates a unique ID
func generateID() string {
	return fmt.Sprintf("user-%d", time.Now().UnixNano())
}

// User represents a user in the system
type User struct {
	ID        string
	Name      string
	Email     string
	CreatedAt time.Time
	UpdatedAt time.Time
}

// UserRepository handles user data storage
type UserRepository struct {
	// Database connection would go here
}

// FindByID finds a user by ID
func (r *UserRepository) FindByID(id string) (*User, error) {
	// Database query logic would go here
	return &User{
		ID:        id,
		Name:      "Test User",
		Email:     "test@example.com",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}, nil
}

// Save saves a user to the database
func (r *UserRepository) Save(user *User) error {
	// Database save logic would go here
	return nil
}

// Logger logs messages
type Logger struct{}

// Info logs an info message
func (l *Logger) Info(message string) {
	fmt.Printf("[INFO] %s\n", message)
}

// Error logs an error message
func (l *Logger) Error(message string) {
	fmt.Printf("[ERROR] %s\n", message)
}