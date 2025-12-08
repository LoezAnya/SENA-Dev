package com.api.nequiclone.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.api.nequiclone.entity.MobileOperator;
import com.api.nequiclone.enums.EntityStatus;

@Repository
public interface MobileOperatorRepository extends JpaRepository<MobileOperator, Long> {

    List<MobileOperator> findAllByStatusTrue();
    Optional<MobileOperator> findByNameAndStatus(String name,EntityStatus status);
    Optional<MobileOperator>  findById(Long id);

}
