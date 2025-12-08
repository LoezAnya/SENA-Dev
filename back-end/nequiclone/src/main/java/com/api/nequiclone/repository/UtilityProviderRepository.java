package com.api.nequiclone.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.api.nequiclone.entity.UtilityProvider;
import com.api.nequiclone.enums.UtilityCategory;

@Repository
public interface UtilityProviderRepository extends JpaRepository<UtilityProvider, Long> {

    // Buscar proveedores activos por categoría
    List<UtilityProvider> findByCategoryAndActiveTrue(UtilityCategory category);

    // Buscar proveedor por nombre y estado activo
    Optional<UtilityProvider> findByNameAndActiveTrue(String name);

    // Buscar todos los proveedores activos
    List<UtilityProvider> findAllByActiveTrue();

    // Buscar proveedor por id
    Optional<UtilityProvider> findById(Long id);
}