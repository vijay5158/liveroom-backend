# Use a Python base image
FROM python:3.9

# Set the working directory
WORKDIR /

# Copy the Django project files into the container
COPY . /

# Install project dependencies
RUN pip install -r requirements.txt

# Expose the necessary ports
EXPOSE 8000

# Start the Django Channels server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
