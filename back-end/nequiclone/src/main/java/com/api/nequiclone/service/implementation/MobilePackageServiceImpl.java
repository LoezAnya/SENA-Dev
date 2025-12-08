package com.api.nequiclone.service.implementation;

import java.util.List;

import org.springframework.stereotype.Service;

import com.api.nequiclone.entity.MobileOperator;
import com.api.nequiclone.entity.MobilePackage;
import com.api.nequiclone.repository.MobileOperatorRepository;
import com.api.nequiclone.repository.MobilePackageRepository;
import com.api.nequiclone.service.interfaces.MobilePackageService;

@Service
public class MobilePackageServiceImpl implements MobilePackageService {

    private final MobileOperatorRepository operatorRepository;
    private final MobilePackageRepository packageRepository;

    public MobilePackageServiceImpl(MobileOperatorRepository operatorRepository,
                                    MobilePackageRepository packageRepository) {
        this.operatorRepository = operatorRepository;
        this.packageRepository = packageRepository;
    }

    /**
     * Devuelve todos los operadores activos.
     */
    @Override
    public List<MobileOperator> getAllActiveOperators() {
        return operatorRepository.findAllByActiveTrue();
    }

    /**
     * Devuelve paquetes por operador.
     */
    @Override
    public List<MobilePackage> getPackagesByOperator(Long operatorId) {
        return packageRepository.findByOperatorId(operatorId);
    }

    /**
     * Devuelve paquete por id (lanza IllegalStateException si no existe).
     */
    @Override
    public MobilePackage getPackageById(Long packageId) {
        return packageRepository.findById(packageId).orElseThrow(() -> new IllegalStateException("Paquete móvil no encontrado: " + packageId));
    }
}