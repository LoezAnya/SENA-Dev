package com.api.nequiclone.service.interfaces;

import java.util.List;

import com.api.nequiclone.entity.MobileOperator;
import com.api.nequiclone.entity.MobilePackage;

public interface MobilePackageService {
    
    List<MobileOperator> getAllActiveOperators();

    List<MobilePackage> getPackagesByOperator(Long operatorId);

    MobilePackage getPackageById(Long packageId);
}
