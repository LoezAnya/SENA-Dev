package com.api.nequiclone.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.api.nequiclone.entity.*;


@Repository
public interface AccountRepository extends JpaRepository<Account, String> {
    
}
