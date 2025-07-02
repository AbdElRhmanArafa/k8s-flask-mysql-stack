FROM mysql:8.0

# Environment variables
ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=flaskapp
ENV MYSQL_USER=flaskuser
ENV MYSQL_PASSWORD=flaskpassword

# Copy database initialization scripts
COPY initdb/ /docker-entrypoint-initdb.d/

# Custom MySQL configuration
COPY my.cnf /etc/mysql/conf.d/my.cnf

# Set permissions
RUN chown -R mysql:mysql /docker-entrypoint-initdb.d/ /etc/mysql/conf.d/

# Expose port
EXPOSE 3306
