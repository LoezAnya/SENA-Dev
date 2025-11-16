package com.api.nequiclone.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.api.nequiclone.entity.User;



@Repository
public interface UserRepository extends JpaRepository<User, Long>{
    Optional<User> findByEmail(String email);
    Optional<User> findByIdentification(String identification);
    Optional<User> findById(Long id);
    Boolean existsByEmail(String email);    
} 
