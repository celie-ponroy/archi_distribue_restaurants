FROM php:8.2-apache

# Install system deps and PHP extensions. We use the mongodb extension via pecl.
RUN apt-get update && apt-get install -y \
    libzip-dev zip libpng-dev libjpeg-dev libfreetype6-dev libonig-dev libxml2-dev \
    libssl-dev pkg-config ca-certificates \
    && docker-php-ext-configure gd --with-jpeg --with-freetype \
    && docker-php-ext-install -j$(nproc) gd zip

# Install PECL mongodb extension
RUN pecl channel-update pecl.php.net \
    && pecl install mongodb || true \
    && docker-php-ext-enable mongodb

# Enable Apache rewrite module
RUN a2enmod rewrite

# Copy default vhost tweaks if you have any (optional)
# COPY ./docker/vhost.conf /etc/apache2/sites-available/000-default.conf

WORKDIR /var/www/html

# In development we mount the source via docker-compose; still copy to image for build contexts
COPY . /var/www/html

# Ensure proper permissions for Apache
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
