package com.api.nequiclone.repository;

import java.util.List;
import java.util.Optional;

import javax.swing.text.html.parser.Entity;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.api.nequiclone.entity.UtilityProvider;
import com.api.nequiclone.enums.EntityStatus;
import com.api.nequiclone.enums.UtilityCategory;

@Repository
public interface UtilityProviderRepository extends JpaRepository<UtilityProvider, Long> {

    
    List<UtilityProvider> findByCategoryAndStatus(UtilityCategory category, EntityStatus status);

   
    Optional<UtilityProvider> findByNameAndStatus(String name, EntityStatus status);

    
    List<UtilityProvider> findAllByStatusTrue();

    
    Optional<UtilityProvider> findById(Long id);
}