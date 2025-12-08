package com.api.nequiclone.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.api.nequiclone.entity.MobileOperator;

@Repository
public interface MobileOperatorRepository extends JpaRepository<MobileOperator, Long> {

    List<MobileOperator> findAllByActiveTrue();
    Optional<MobileOperator> findByNameAndActiveTrue(String name);
    Optional<MobileOperator>  findById(Long id);

}
