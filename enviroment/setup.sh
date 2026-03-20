#!/bin/bash
# Script unificado para configurar Hyperledger Fabric
# Uso: ./setup.sh

set -e

DOMAIN="net"
CHANNEL_NAME="mychannel"
NETWORK_NAME="fabric"

echo "=============================================="
echo "  Hyperledger Fabric - Configuración"
echo "=============================================="

# Variables
export PATH="$(pwd)/bin:$PATH"

# 1. Crear estructura de directorios
echo ""
echo ">> Creando estructura de directorios..."
mkdir -p channel-artifacts
mkdir -p organizations/peerOrganizations
mkdir -p organizations/ordererOrganizations

# 2. Generar certificados
echo ""
echo ">> Generando certificados..."
cat > crypto-config-template.yaml << 'EOF'
OrdererOrgs:
  - Name: Orderer
    Domain: ORDERER_DOMAIN
    Specs:
      - Hostname: orderer

PeerOrgs:
  - Name: Org1
    Domain: PEER_DOMAIN
    Template:
      Count: 1
    Users:
      Count: 1
EOF

sed -e "s/ORDERER_DOMAIN/${DOMAIN}/g" -e "s/PEER_DOMAIN/org1.${DOMAIN}/g" \
    crypto-config-template.yaml > crypto-config.yaml
rm crypto-config-template.yaml

cryptogen generate --config=./crypto-config.yaml --output=./organizations
echo "✓ Certificados generados"

# Agregar config.yaml a los MSP (sin NodeOUs para evitar problemas de validacion)
echo ""
echo ">> Agregando config.yaml a MSP..."
cat > organizations/peerOrganizations/org1.net/msp/config.yaml << 'EOF'
NodeOUs:
  Enable: false
EOF

cat > organizations/ordererOrganizations/net/msp/config.yaml << 'EOF'
NodeOUs:
  Enable: false
EOF

cat > organizations/ordererOrganizations/net/orderers/orderer.net/msp/config.yaml << 'EOF'
NodeOUs:
  Enable: false
EOF

# Copiar Org1 MSP a la carpeta del orderer para el consortium
mkdir -p organizations/ordererOrganizations/${DOMAIN}/orderers/orderer.${DOMAIN}/msp/consortiums
cp -r organizations/peerOrganizations/org1.${DOMAIN}/msp/* organizations/ordererOrganizations/${DOMAIN}/orderers/orderer.${DOMAIN}/msp/consortiums/

echo "✓ config.yaml agregado"

# 3. Generar configtx.yaml
echo ""
echo ">> Generando configtx.yaml..."

cat > configtx.yaml << EOF
Organizations:
  - &OrdererOrg
    Name: OrdererOrg
    ID: OrdererMSP
    MSPDir: organizations/ordererOrganizations/${DOMAIN}/orderers/orderer.${DOMAIN}/msp
    Policies:
      Readers:
        Type: Signature
        Rule: "OR('OrdererOrg.member')"
      Writers:
        Type: Signature
        Rule: "OR('OrdererOrg.member')"
      Admins:
        Type: Signature
        Rule: "OR('OrdererOrg.admin')"
    OrdererEndpoints:
      - orderer.${DOMAIN}:7050

  - &Org1
    Name: Org1MSP
    ID: Org1MSP
    MSPDir: organizations/peerOrganizations/org1.${DOMAIN}/msp
    Policies:
      Readers:
        Type: Signature
        Rule: "OR('Org1MSP.member')"
      Writers:
        Type: Signature
        Rule: "OR('Org1MSP.member')"
      Admins:
        Type: Signature
        Rule: "OR('Org1MSP.admin')"
    AnchorPeers:
      - Host: peer0.org1.${DOMAIN}
        Port: 7051

Capabilities:
  Channel: &ChannelCapabilities
    V2_0: true
  Orderer: &OrdererCapabilities
    V2_0: true
  Application: &ApplicationCapabilities
    V2_0: true

Application: &ApplicationDefaults
  Organizations:
  Policies:
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
    LifecycleEndorsement:
      Type: ImplicitMeta
      Rule: "MAJORITY Endorsement"
    Endorsement:
      Type: ImplicitMeta
      Rule: "MAJORITY Endorsement"
  Capabilities:
    <<: *ApplicationCapabilities

Orderer: &OrdererDefaults
  Addresses:
    - orderer.${DOMAIN}:7050
  BatchTimeout: 2s
  BatchSize:
    MaxMessageCount: 10
    AbsoluteMaxBytes: 99 MB
    PreferredMaxBytes: 512 KB
  Organizations:
  Policies:
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
    BlockValidation:
      Type: ImplicitMeta
      Rule: "ANY Writers"

Channel: &ChannelDefaults
  Policies:
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
  Capabilities:
    <<: *ChannelCapabilities

Profiles:
  ChannelProfile:
    <<: *ChannelDefaults
    Consortium: SampleConsortium
    Orderer:
      <<: *OrdererDefaults
      Organizations:
        - *OrdererOrg
      Capabilities: *OrdererCapabilities
    Application:
      <<: *ApplicationDefaults
      Organizations:
        - *Org1
      Capabilities: *ApplicationCapabilities

  GenesisProfile:
    <<: *ChannelDefaults
    Consortiums:
      SampleConsortium:
        Organizations:
          - *Org1
    Orderer:
      <<: *OrdererDefaults
      OrdererType: solo
      Organizations:
        - *OrdererOrg
      Capabilities: *OrdererCapabilities
    Application:
      <<: *ApplicationDefaults
      Organizations:
        - *Org1
EOF

echo "✓ configtx.yaml generado"

# 4. Generar artefactos del canal
echo ""
echo ">> Generando bloque de genesis..."
configtxgen -profile GenesisProfile -channelID ${CHANNEL_NAME} -outputBlock ./channel-artifacts/genesis.block

echo ">> Generando transacción del canal..."
configtxgen -profile ChannelProfile -channelID ${CHANNEL_NAME} -outputCreateChannelTx ./channel-artifacts/channel.tx -asOrg Org1MSP

echo ">> Generando anchor peer..."
configtxgen -profile ChannelProfile -channelID ${CHANNEL_NAME} -outputAnchorPeersUpdate ./channel-artifacts/Org1MSPanchors.tx -asOrg Org1MSP

echo "✓ Artefactos del canal generados"

# 5. Preparar chaincode
echo ""
echo ">> Preparando chaincode..."
cat > chaincode/tasks/go.mod << 'EOF'
module tasks

go 1.20

require (
	github.com/hyperledger/fabric-chaincode-go v0.0.0-20240704073638-9fb89180dc17
	github.com/hyperledger/fabric-protos-go v0.3.4
)

require (
	github.com/golang/protobuf v1.5.4 // indirect
	golang.org/x/net v0.25.0 // indirect
	golang.org/x/sys v0.20.0 // indirect
	golang.org/x/text v0.15.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20240528184218-531527333157 // indirect
	google.golang.org/grpc v1.65.0 // indirect
	google.golang.org/protobuf v1.34.1 // indirect
)
EOF

# Crear go.sum
cat > chaincode/tasks/go.sum << 'EOF'
github.com/golang/protobuf v1.5.4 h1:i+1DLAR9jnY1NYknH1I49Mn6C/qJu1YP2KrLSiY58LE=
github.com/golang/protobuf v1.5.4/go.mod h1:FDviiEEYAqOTN1qk5qPZLJOCB1iPK4eH7xNU4s8wqE0=
github.com/hyperledger/fabric-chaincode-go v0.0.0-20240704073638-9fb89180dc17 h1:GNgBBsJwi7eJLHj1Q3h3JPhQ9L3M/I8S5gWxG8k+nmU=
github.com/hyperledger/fabric-chaincode-go v0.0.0-20240704073638-9fb89180dc17/go.mod h1:R1NwJVGFv6q7XThPQNOpA7r7LnDEvT3oL9fL6ZVy4k=
github.com/hyperledger/fabric-protos-go v0.3.4 h1:x7V9D/7FUBGxdLJC3hHHkIIgL2c3zCm+bGVU0WlnC0=
github.com/hyperledger/fabric-protos-go v0.3.4/go.mod h1:SoDBg8qFOj5NGq3aAyJ18SwPs5S7v1A4/1q8T1N3N4M=
golang.org/x/net v0.25.0 h1:d/OCCoBEUq33pjydKrGQhw7IlUPI2Oylr+8qLx49kac=
golang.org/x/net v0.25.0/go.mod h1:d/xM4en7r/Q+9OCfPYkgFlpYWC2FZAi+3dKnlrHLt3w=
golang.org/x/sys v0.20.0 h1:Od9JTbYCk261bKm4M/mw7AklTlFYIa0bIp9BgSm1S8Y=
golang.org/x/sys v0.20.0/go.mod h1:spTPH65R69YU52JKQLRjTCi6TwRIinn4Dq6v/BRf5c=
golang.org/x/text v0.15.0 h1:r4lAV3LKovZfc4jgY/2pE/rfY2j3qivPcpRsz+tC2k=
golang.org/x/text v0.15.0/go.mod h1:TvPlkPrEEE2Kf3VCq5PNNAaepxhECSNASy2MaLC2nqo=
google.golang.org/genproto/googleapis/rpc v0.0.0-20240528184218-531527333157 h1:qpOXX8twZmqS4+Tj6NqQcZMpT8R0y3RPlqIl8m3F2TU=
google.golang.org/genproto/googleapis/rpc v0.0.0-20240528184218-531527333157/go.mod h1:AFq4HBPMcMVK9uxOkwVnv4s+Nm2VIHTJfZBzpXN6HH8=
google.golang.org/grpc v1.65.0 h1:bs/cUb4lp1G5iImFFd3u5ixQzweKizoZJAwBNLR42lc=
google.golang.org/grpc v1.65.0/go.mod h1:W4TteufgZHEv4x9XkNoPmF4T25sN2rWC+sM5G1C4u4=
google.golang.org/protobuf v1.34.1 h1:9fZABiNV8rm5jA+5x4y3z0dxmvqDiThAHl5oU3tlvMM=
google.golang.org/protobuf v1.34.1/go.mod h1:qL4bnVvlV8jUNCHYFm2y4NUa4Gbc2QvIT6a6k1KHlPQ=
EOF
echo "✓ Chaincode preparado"

# 6. Guardar variables en archivo para otros scripts
cat > .env << EOF
DOMAIN=${DOMAIN}
CHANNEL_NAME=${CHANNEL_NAME}
ORDERER_HOST=orderer.${DOMAIN}
ORDERER_PORT=7050
PEER_HOST=peer0.org1.${DOMAIN}
PEER_PORT=7051
EOF

echo ""
echo "=============================================="
echo "  ✓ Configuración completada"
echo "=============================================="
echo ""
echo "Dominio: ${DOMAIN}"
echo "Canal: ${CHANNEL_NAME}"
echo ""
echo "Próximos pasos:"
echo "  make up      # Levantar la red"
echo "  make down    # Bajar la red"
