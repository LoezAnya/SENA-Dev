package com.api.nequiclone.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.api.nequiclone.entity.MobilePackage;
@Repository
public interface MobilePackageRepository extends JpaRepository<MobilePackage, Long> {

    List<MobilePackage> findByOperatorId(Long operatorId);

    Optional<MobilePackage> findById(Long packageId);

}
