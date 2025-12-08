package com.api.nequiclone.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.api.nequiclone.entity.MobilePackage;

public interface MobilePackageRepository extends JpaRepository<MobilePackage, Long> {

    List<MobilePackage> findByOperatorId(Long operatorId);

    Optional<MobilePackage> findById(Long packageId);

}
